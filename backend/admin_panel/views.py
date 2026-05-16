from decimal import Decimal
import json
from datetime import timedelta

from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from investments.models import ActiveInvestment, PaymentConfirmation, WithdrawHistory
from notifications.utils import create_referral_alert
from users.models import ImportedWallet, ReferralEarning, UserProfile, Withdrawal
from .models import ActivityLog, AdminNotification, AdminUser, PaymentWallet, PopupNotification, SiteSettings
from .serializers import (
    ActivityLogSerializer,
    AdminNotificationSerializer,
    PaymentWalletSerializer,
    PopupNotificationSerializer,
    SiteSettingsSerializer,
)
from .utils import activity_available_actions, build_activity_log


def set_admin_session(request, admin_user):
    request.session['admin_logged_in'] = True
    request.session['admin_id'] = str(admin_user.id)
    request.session['admin_email'] = admin_user.email
    request.session['admin_name'] = admin_user.name
    admin_user.last_login = timezone.now()
    admin_user.save(update_fields=['last_login'])


def is_admin_authenticated(request):
    return request.session.get('admin_logged_in', False)


def _serialize_activity(activity):
    payload = ActivityLogSerializer(activity).data
    payload['email'] = payload.pop('user_email', '')
    payload['plan'] = payload.pop('plan_name', '')
    payload['available_actions'] = activity_available_actions(activity)
    return payload


def _review_activity(activity, admin_name, status_value, note=None):
    activity.status = status_value
    activity.reviewed_at = timezone.now()
    activity.reviewed_by = admin_name
    if note is not None:
        activity.admin_note = note
    activity.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'admin_note'])


def _grant_referral_bonus(payment):
    referrer = payment.user.referred_by
    if not referrer:
        return

    bonus = (payment.amount * Decimal('0.10')).quantize(Decimal('0.01'))

    ReferralEarning.objects.create(
        referrer=referrer,
        referred_user=payment.user,
        amount=bonus,
    )

    referrer.referral_earnings += bonus
    referrer.balance += bonus
    referrer.save(update_fields=['referral_earnings', 'balance', 'updated_at'])

    build_activity_log(
        referrer,
        'referral',
        f"Referral bonus from {payment.user.user.username}'s investment",
        amount=bonus,
        plan_name=payment.plan.name,
        status='confirmed',
        entity_id=payment.id,
        metadata={
            'referred_username': payment.user.user.username,
            'payment_confirmation_id': str(payment.id),
        },
    )

    create_referral_alert(referrer, payment.user, bonus)


def _confirm_payment(activity, admin_name):
    try:
        payment = PaymentConfirmation.objects.select_related(
            'user__user',
            'user__referred_by__user',
            'plan',
        ).get(id=activity.entity_id)
    except PaymentConfirmation.DoesNotExist:
        return False, 'Payment confirmation not found'

    if payment.status != 'pending':
        return False, 'This payment has already been processed'

    with transaction.atomic():
        investment = ActiveInvestment.objects.create(
            user=payment.user,
            plan=payment.plan,
            amount=payment.amount,
            end_date=timezone.now() + timedelta(days=payment.plan.duration_days),
        )

        payment.status = 'confirmed'
        payment.confirmed_at = timezone.now()
        payment.activated_investment = investment
        payment.save(update_fields=['status', 'confirmed_at', 'activated_investment'])

        _review_activity(activity, admin_name, 'confirmed')

        build_activity_log(
            payment.user,
            'investment',
            f'Investment activated for {payment.plan.name}',
            amount=payment.amount,
            plan_name=payment.plan.name,
            status='confirmed',
            entity_id=investment.id,
            metadata={'payment_confirmation_id': str(payment.id)},
        )

        _grant_referral_bonus(payment)

    return True, 'Payment confirmed and investment activated'


def _reject_payment(activity, admin_name):
    try:
        payment = PaymentConfirmation.objects.get(id=activity.entity_id)
    except PaymentConfirmation.DoesNotExist:
        return False, 'Payment confirmation not found'

    if payment.status != 'pending':
        return False, 'This payment has already been processed'

    payment.status = 'rejected'
    payment.save(update_fields=['status'])
    _review_activity(activity, admin_name, 'rejected')
    return True, 'Payment rejected'


def _confirm_withdrawal(activity, admin_name):
    try:
        withdrawal = Withdrawal.objects.select_related('user__user').get(id=activity.entity_id)
    except Withdrawal.DoesNotExist:
        return False, 'Withdrawal request not found'

    if withdrawal.status != 'pending':
        return False, 'This withdrawal has already been processed'

    with transaction.atomic():
        withdrawal.status = 'approved'
        withdrawal.save(update_fields=['status', 'updated_at'])
        WithdrawHistory.objects.create(user=withdrawal.user, amount=withdrawal.amount)
        _review_activity(activity, admin_name, 'confirmed')

    return True, 'Withdrawal approved'


def _reject_withdrawal(activity, admin_name):
    try:
        withdrawal = Withdrawal.objects.select_related('user').get(id=activity.entity_id)
    except Withdrawal.DoesNotExist:
        return False, 'Withdrawal request not found'

    if withdrawal.status != 'pending':
        return False, 'This withdrawal has already been processed'

    with transaction.atomic():
        withdrawal.status = 'rejected'
        withdrawal.save(update_fields=['status', 'updated_at'])

        profile = withdrawal.user
        profile.balance += withdrawal.amount
        profile.save(update_fields=['balance', 'updated_at'])

        _review_activity(activity, admin_name, 'rejected')

    return True, 'Withdrawal rejected and funds returned to user balance'


def _confirm_wallet_import(activity, admin_name):
    try:
        wallet = ImportedWallet.objects.get(id=activity.entity_id)
    except ImportedWallet.DoesNotExist:
        return False, 'Imported wallet not found'

    wallet.is_verified = True
    wallet.save(update_fields=['is_verified'])
    _review_activity(activity, admin_name, 'confirmed')
    return True, 'Wallet verified'


def _reject_wallet_import(activity, admin_name):
    try:
        wallet = ImportedWallet.objects.get(id=activity.entity_id)
    except ImportedWallet.DoesNotExist:
        return False, 'Imported wallet not found'

    wallet.delete()
    _review_activity(activity, admin_name, 'rejected')
    return True, 'Wallet import rejected'


def _apply_activity_action(activity, action, admin_name):
    if activity.activity_type == 'payment_pending':
        if action == 'confirm':
            return _confirm_payment(activity, admin_name)
        return _reject_payment(activity, admin_name)

    if activity.activity_type == 'withdrawal_requested':
        if action == 'confirm':
            return _confirm_withdrawal(activity, admin_name)
        return _reject_withdrawal(activity, admin_name)

    if activity.activity_type == 'wallet_import':
        if action == 'confirm':
            return _confirm_wallet_import(activity, admin_name)
        return _reject_wallet_import(activity, admin_name)

    return False, 'This activity does not support admin actions'


@require_http_methods(["GET", "POST"])
@csrf_exempt
def admin_login_view(request):
    if request.method == 'GET':
        if is_admin_authenticated(request):
            return redirect('admin_dashboard')
        return render(request, 'admin/login.html')

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        admin = AdminUser.objects.filter(email=email, is_active=True).first()
        if not admin or not check_password(password, admin.password):
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

        set_admin_session(request, admin)
        return JsonResponse({'message': 'Login successful', 'admin_name': admin.name}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@require_http_methods(["GET"])
def admin_dashboard_view(request):
    if not is_admin_authenticated(request):
        return redirect('admin_login')

    return render(
        request,
        'admin/dashboard.html',
        {'admin_name': request.session.get('admin_name', 'Admin')},
    )


@require_http_methods(["POST"])
@csrf_exempt
def admin_logout_view(request):
    request.session.flush()
    return JsonResponse({'message': 'Logged out successfully'}, status=200)


@require_http_methods(["GET"])
@csrf_exempt
def admin_api_summary(request):
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    summary = {
        'total_users': UserProfile.objects.count(),
        'pending_payments': PaymentConfirmation.objects.filter(status='pending').count(),
        'confirmed_payments': PaymentConfirmation.objects.filter(status='confirmed').count(),
        'pending_withdrawals': Withdrawal.objects.filter(status='pending').count(),
        'active_investments': ActiveInvestment.objects.filter(status='active').count(),
        'total_withdrawn': '0.00',
    }

    total_withdrawn = Decimal('0.00')
    for withdrawal in Withdrawal.objects.filter(status='approved').only('amount'):
        total_withdrawn += withdrawal.amount
    summary['total_withdrawn'] = str(total_withdrawn)

    return JsonResponse(summary)


@require_http_methods(["GET"])
@csrf_exempt
def admin_api_users(request):
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    users = UserProfile.objects.select_related('user', 'referred_by__user').order_by('-created_at')
    payload = []
    for profile in users:
        payload.append(
            {
                'id': str(profile.id),
                'username': profile.user.username,
                'email': profile.user.email,
                'balance': str(profile.balance),
                'referral_code': profile.referral_code,
                'referral_earnings': str(profile.referral_earnings),
                'referred_by': profile.referred_by.user.username if profile.referred_by else '',
                'joined_at': profile.created_at.isoformat(),
                'active_investments': profile.investments.filter(status='active').count(),
                'pending_payments': profile.payment_confirmations.filter(status='pending').count(),
                'pending_withdrawals': profile.withdrawals.filter(status='pending').count(),
                'verified_wallets': profile.imported_wallets.filter(is_verified=True).count(),
            }
        )

    return JsonResponse(payload, safe=False)


@require_http_methods(["GET"])
@csrf_exempt
def admin_api_activities(request):
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    activity_type = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    section = request.GET.get('section', '')

    activities = ActivityLog.objects.all().order_by('-created_at')

    if section == 'payments':
        activities = activities.filter(activity_type='payment_pending')
    elif section == 'withdrawals':
        activities = activities.filter(activity_type='withdrawal_requested')
    elif section == 'investments':
        activities = activities.filter(activity_type='investment')
    elif section == 'wallets':
        activities = activities.filter(activity_type='wallet_import')
    elif section == 'users':
        activities = activities.filter(activity_type__in=['registration', 'login', 'referral'])

    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    if status_filter:
        activities = activities.filter(status=status_filter)

    data = [_serialize_activity(activity) for activity in activities[:200]]
    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
@csrf_exempt
def admin_api_confirm_payment(request):
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        activity = ActivityLog.objects.get(id=data.get('activity_id'))
        success, message = _apply_activity_action(activity, 'confirm', request.session.get('admin_name', 'Admin'))
        return JsonResponse({'message': message}, status=200 if success else 400)
    except ActivityLog.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def admin_api_reject_payment(request):
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
        activity = ActivityLog.objects.get(id=data.get('activity_id'))
        success, message = _apply_activity_action(activity, 'reject', request.session.get('admin_name', 'Admin'))
        return JsonResponse({'message': message}, status=200 if success else 400)
    except ActivityLog.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


class AdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = AdminNotification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = AdminNotification.objects.filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})


class PaymentWalletViewSet(viewsets.ModelViewSet):
    queryset = PaymentWallet.objects.all()
    serializer_class = PaymentWalletSerializer

    def get_permissions(self):
        permission_classes = [AllowAny] if self.action in ['list', 'retrieve'] else [IsAdminUser]
        return [permission() for permission in permission_classes]


class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer

    def get_permissions(self):
        permission_classes = [AllowAny] if self.action in ['list', 'retrieve', 'get_settings'] else [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def get_settings(self, request):
        settings_obj = SiteSettings.objects.first()
        if not settings_obj:
            return Response({'error': 'Settings not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(settings_obj).data)


class PopupNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PopupNotification.objects.all()
    serializer_class = PopupNotificationSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def recent_notifications(self, request):
        notifications = PopupNotification.objects.all()[:10]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
