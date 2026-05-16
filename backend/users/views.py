from decimal import Decimal, InvalidOperation
import random
import string
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from admin_panel.serializers import ActivityLogSerializer
from admin_panel.models import ActivityLog
from admin_panel.utils import build_activity_log
from investments.serializers import (
    ActiveInvestmentSerializer,
    CopyTradingFollowerSerializer,
    CryptoSwapSerializer,
    PaymentConfirmationSerializer,
)
from investments.utils import sync_user_investment_earnings
from investments.models import ActiveInvestment, CopyTradingFollower, CryptoSwap, PaymentConfirmation
from .models import ImportedWallet, ReferralEarning, UserProfile, Withdrawal
from .serializers import (
    ImportedWalletSerializer,
    ReferralEarningSerializer,
    UserProfileSerializer,
    UserSerializer,
    WithdrawalSerializer,
)


def generate_referral_code():
    while True:
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not UserProfile.objects.filter(referral_code=referral_code).exists():
            return referral_code


class UserRegistrationView(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            username = request.data.get('username', '').strip()
            email = request.data.get('email', '').strip().lower()
            password = request.data.get('password', '').strip()
            transaction_pin = request.data.get('transaction_pin', '').strip()
            referral_code = request.data.get('referral_code') or None

            if not username or not password or not transaction_pin:
                return Response(
                    {'error': 'Username, password, and PIN are required'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(username) < 3:
                return Response({'error': 'Username must be at least 3 characters'}, status=status.HTTP_400_BAD_REQUEST)

            if len(transaction_pin) != 4 or not transaction_pin.isdigit():
                return Response({'error': 'Transaction PIN must be 4 digits'}, status=status.HTTP_400_BAD_REQUEST)

            if len(password) < 4:
                return Response({'error': 'Password must be at least 4 characters'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if email and User.objects.filter(email__iexact=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            referred_profile = None
            if referral_code:
                referred_profile = UserProfile.objects.filter(referral_code=referral_code).first()

            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password)
                profile = UserProfile.objects.create(
                    user=user,
                    transaction_pin=transaction_pin,
                    referral_code=generate_referral_code(),
                    referred_by=referred_profile,
                )

                build_activity_log(
                    user,
                    'registration',
                    'User account created',
                    status='confirmed',
                    entity_id=user.id,
                    metadata={
                        'referral_code': profile.referral_code,
                        'referred_by': referred_profile.referral_code if referred_profile else None,
                    },
                )

            return Response(
                {
                    'message': 'User registered successfully',
                    'user_id': user.id,
                    'username': user.username,
                    'referral_code': profile.referral_code,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return Response({'error': f'Registration failed: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            username = request.data.get('username', '').strip()
            password = request.data.get('password', '').strip()

            if not username or not password:
                return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, username=username, password=password)
            if user is None:
                return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            profile = UserProfile.objects.select_related('user').get(user=user)

            build_activity_log(
                user,
                'login',
                'User logged in successfully',
                status='confirmed',
                entity_id=user.id,
            )

            return Response(
                {
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'profile': UserProfileSerializer(profile).data,
                },
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response({'error': f'Login failed: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        try:
            username = request.data.get('username', '').strip()
            email = request.data.get('email', '').strip().lower()

            user = User.objects.filter(username=username).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if email and user.email and user.email.lower() != email:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': 'User verified'}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        try:
            username = request.data.get('username', '').strip()
            email = request.data.get('email', '').strip().lower()
            new_password = request.data.get('new_password', '')

            if not new_password or len(new_password) < 4:
                return Response({'error': 'Password must be at least 4 characters'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(username=username).first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            if email and user.email and user.email.lower() != email:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user.set_password(new_password)
            user.save(update_fields=['password'])

            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WithdrawalViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(user=self.request.user.profile).order_by('-created_at')

    def create(self, request):
        user_profile = request.user.profile
        method = request.data.get('method')
        crypto_type = request.data.get('crypto_type')
        network = request.data.get('network')
        wallet_address = request.data.get('wallet_address')
        bank_details = request.data.get('bank_details')

        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Enter a valid withdrawal amount'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'error': 'Withdrawal amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        if amount > user_profile.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        if method not in {'crypto', 'bank'}:
            return Response({'error': 'Select a valid withdrawal method'}, status=status.HTTP_400_BAD_REQUEST)

        if method == 'crypto' and (not crypto_type or not wallet_address or not network):
            return Response(
                {'error': 'Crypto withdrawals require crypto type, network, and destination wallet address'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if method == 'bank' and not bank_details:
            return Response({'error': 'Bank details are required for bank withdrawals'}, status=status.HTTP_400_BAD_REQUEST)

        latest_withdrawal = Withdrawal.objects.filter(
            user=user_profile,
            status__in=['pending', 'approved'],
        ).order_by('-created_at').first()

        if latest_withdrawal:
            next_allowed_at = latest_withdrawal.created_at + timedelta(days=30)
        else:
            first_investment = ActiveInvestment.objects.filter(user=user_profile).order_by('start_date').first()
            if not first_investment:
                return Response(
                    {'error': 'You need an active investment before requesting a withdrawal'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            next_allowed_at = first_investment.start_date + timedelta(days=30)

        if timezone.now() < next_allowed_at:
            formatted_date = timezone.localtime(next_allowed_at).strftime('%B %d, %Y')
            return Response(
                {'error': f'Withdrawal is not available yet. Your next withdrawal date is {formatted_date}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user_profile.balance -= amount
            user_profile.save(update_fields=['balance', 'updated_at'])

            withdrawal = Withdrawal.objects.create(
                user=user_profile,
                amount=amount,
                method=method,
                crypto_type=crypto_type if method == 'crypto' else None,
                network=network if method == 'crypto' else None,
                wallet_address=wallet_address if method == 'crypto' else None,
                bank_details=bank_details if method == 'bank' else None,
            )

            build_activity_log(
                user_profile,
                'withdrawal_requested',
                f'Withdrawal request submitted via {method.upper()} {crypto_type or ""} {network or ""}'.strip(),
                amount=amount,
                status='pending',
                entity_id=withdrawal.id,
                metadata={
                    'method': method,
                    'crypto_type': crypto_type,
                    'network': network,
                    'wallet_address': wallet_address,
                    'bank_details': bank_details,
                },
            )

        return Response(
            {
                'message': 'Withdrawal request submitted. Awaiting admin approval.',
                'withdrawal': WithdrawalSerializer(withdrawal).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def history(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ReferralViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReferralEarningSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReferralEarning.objects.filter(referrer=self.request.user.profile).select_related(
            'referrer__user',
            'referred_user__user',
        ).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def my_referrals(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.GenericViewSet):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = request.user.profile
        return Response(
            {
                'user': UserSerializer(request.user).data,
                'profile': UserProfileSerializer(profile).data,
            }
        )

    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        profile = request.user.profile
        sync_user_investment_earnings(profile)
        profile.refresh_from_db()

        investments = ActiveInvestment.objects.filter(user=profile).select_related('plan').order_by('-start_date')
        referrals = self.request.user.profile.referral_earnings_made.select_related(
            'referred_user__user',
            'referrer__user',
        ).order_by('-created_at')
        withdrawals = Withdrawal.objects.filter(user=profile).order_by('-created_at')
        payments = PaymentConfirmation.objects.filter(user=profile).select_related('plan').order_by('-created_at')
        copy_allocations = CopyTradingFollower.objects.filter(
            follower=profile,
            is_active=True,
        ).select_related('copy_trading_profile__trader__user').order_by('-created_at')
        swaps = CryptoSwap.objects.filter(user=profile).order_by('-created_at')
        imported_wallets = ImportedWallet.objects.filter(user=profile).order_by('-created_at')
        activities = ActivityLog.objects.filter(username=request.user.username).order_by('-created_at')[:100]

        total_earned = sum((investment.earned for investment in investments), Decimal('0.00'))

        return Response(
            {
                'user': UserSerializer(request.user).data,
                'profile': UserProfileSerializer(profile).data,
                'stats': {
                    'active_investments': investments.filter(status='active').count(),
                    'total_earned': str(total_earned),
                    'total_referrals': referrals.count(),
                    'pending_payments': payments.filter(status='pending').count(),
                    'pending_withdrawals': withdrawals.filter(status='pending').count(),
                },
                'investments': ActiveInvestmentSerializer(investments, many=True).data,
                'referrals': ReferralEarningSerializer(referrals, many=True).data,
                'withdrawals': WithdrawalSerializer(withdrawals, many=True).data,
                'payment_confirmations': PaymentConfirmationSerializer(payments, many=True).data,
                'copy_allocations': CopyTradingFollowerSerializer(copy_allocations, many=True).data,
                'swaps': CryptoSwapSerializer(swaps, many=True).data,
                'imported_wallets': ImportedWalletSerializer(imported_wallets, many=True).data,
                'activities': ActivityLogSerializer(activities, many=True).data,
            }
        )

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        current_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        if len(new_password) < 4:
            return Response({'error': 'Password must be at least 4 characters'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])
        update_session_auth_hash(request, request.user)

        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def update_pin(self, request):
        profile = request.user.profile
        current_pin = request.data.get('current_pin', '')
        new_pin = request.data.get('new_pin', '')

        if profile.transaction_pin != current_pin:
            return Response({'error': 'Current PIN is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        if len(new_pin) != 4 or not new_pin.isdigit():
            return Response({'error': 'PIN must be 4 digits'}, status=status.HTTP_400_BAD_REQUEST)

        profile.transaction_pin = new_pin
        profile.save(update_fields=['transaction_pin', 'updated_at'])

        return Response({'message': 'PIN updated successfully'}, status=status.HTTP_200_OK)


class ImportedWalletViewSet(viewsets.ModelViewSet):
    serializer_class = ImportedWalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ImportedWallet.objects.filter(user=self.request.user.profile).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def import_wallet(self, request):
        user_profile = request.user.profile
        wallet_type = request.data.get('wallet_type')
        wallet_address = request.data.get('wallet_address')

        if not wallet_type or not wallet_address:
            return Response({'error': 'Wallet type and address required'}, status=status.HTTP_400_BAD_REQUEST)

        if ImportedWallet.objects.filter(user=user_profile, wallet_address=wallet_address).exists():
            return Response({'error': 'Wallet already imported'}, status=status.HTTP_400_BAD_REQUEST)

        wallet = ImportedWallet.objects.create(
            user=user_profile,
            wallet_address=wallet_address,
            wallet_type=wallet_type,
            is_verified=False,
        )

        build_activity_log(
            user_profile,
            'wallet_import',
            f'Imported {wallet_type} wallet for verification',
            status='pending',
            entity_id=wallet.id,
            metadata={'wallet_type': wallet_type, 'wallet_address': wallet_address},
        )

        return Response(
            {
                'message': 'Wallet imported. Pending admin verification.',
                'wallet': ImportedWalletSerializer(wallet).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def my_wallets(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
