from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import AdminUser, AdminNotification, PaymentWallet, SiteSettings, PopupNotification, ActivityLog
from .serializers import AdminNotificationSerializer, PaymentWalletSerializer, SiteSettingsSerializer, PopupNotificationSerializer

# Admin Session management
def set_admin_session(request, admin_user):
    request.session['admin_logged_in'] = True
    request.session['admin_id'] = str(admin_user.id)
    request.session['admin_email'] = admin_user.email
    request.session['admin_name'] = admin_user.name
    admin_user.last_login = timezone.now()
    admin_user.save()

def is_admin_authenticated(request):
    return request.session.get('admin_logged_in', False)

@require_http_methods(["GET", "POST"])
@csrf_exempt
def admin_login_view(request):
    """Custom admin login page"""
    if request.method == 'GET':
        if is_admin_authenticated(request):
            return redirect('admin_dashboard')
        return render(request, 'admin/login.html')
    
    # POST request
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        admin = AdminUser.objects.filter(email=email, is_active=True).first()
        
        if not admin:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        
        # Check password
        if not check_password(password, admin.password):
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        
        # Set session
        set_admin_session(request, admin)
        
        return JsonResponse({
            'message': 'Login successful',
            'admin_name': admin.name
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def admin_dashboard_view(request):
    """Custom admin dashboard"""
    if not is_admin_authenticated(request):
        return redirect('admin_login')
    
    context = {
        'admin_name': request.session.get('admin_name', 'Admin'),
    }
    return render(request, 'admin/dashboard.html', context)

@require_http_methods(["POST"])
@csrf_exempt
def admin_logout_view(request):
    """Admin logout"""
    request.session.flush()
    return JsonResponse({'message': 'Logged out successfully'}, status=200)

@require_http_methods(["GET"])
@csrf_exempt
def admin_api_activities(request):
    """Get all activities for admin"""
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    activity_type = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    
    activities = ActivityLog.objects.all()
    
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    if status_filter:
        activities = activities.filter(status=status_filter)
    
    data = [{
        'id': str(a.id),
        'username': a.username,
        'email': a.user_email,
        'activity_type': a.activity_type,
        'description': a.description,
        'amount': str(a.amount) if a.amount else None,
        'plan': a.plan_name,
        'status': a.status,
        'created_at': a.created_at.isoformat(),
    } for a in activities[:50]]
    
    return JsonResponse(data, safe=False)

@require_http_methods(["POST"])
@csrf_exempt
def admin_api_confirm_payment(request):
    """Confirm pending payment"""
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        
        activity = ActivityLog.objects.get(id=activity_id)
        activity.status = 'confirmed'
        activity.save()
        
        return JsonResponse({'message': 'Payment confirmed'}, status=200)
    except ActivityLog.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def admin_api_reject_payment(request):
    """Reject pending payment"""
    if not is_admin_authenticated(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        
        activity = ActivityLog.objects.get(id=activity_id)
        activity.status = 'rejected'
        activity.save()
        
        return JsonResponse({'message': 'Payment rejected'}, status=200)
    except ActivityLog.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        notification.save()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

class PaymentWalletViewSet(viewsets.ModelViewSet):
    queryset = PaymentWallet.objects.all()
    serializer_class = PaymentWalletSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def get_settings(self, request):
        try:
            settings = SiteSettings.objects.first()
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        except SiteSettings.DoesNotExist:
            return Response({'error': 'Settings not found'}, status=status.HTTP_404_NOT_FOUND)

class PopupNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PopupNotification.objects.all()
    serializer_class = PopupNotificationSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def recent_notifications(self, request):
        notifications = PopupNotification.objects.all()[:10]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
