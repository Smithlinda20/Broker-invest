from decimal import Decimal, InvalidOperation
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admin_panel.utils import build_activity_log
from .models import (
    ActiveInvestment,
    CopyTradingFollower,
    CopyTradingProfile,
    CryptoSwap,
    InvestmentPlan,
    PaymentConfirmation,
    WithdrawHistory,
)
from .serializers import (
    ActiveInvestmentSerializer,
    CopyTradingFollowerSerializer,
    CryptoSwapSerializer,
    InvestmentPlanSerializer,
    PaymentConfirmationSerializer,
    WithdrawHistorySerializer,
)
from .utils import sync_user_investment_earnings


class InvestmentPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvestmentPlan.objects.filter(is_active=True).order_by('min_amount')
    serializer_class = InvestmentPlanSerializer
    permission_classes = []


class ActiveInvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = ActiveInvestmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ActiveInvestment.objects.filter(user=self.request.user.profile).select_related('plan').order_by('-start_date')

    def create(self, request):
        return Response(
            {'error': 'Direct investment creation is disabled. Submit a payment confirmation instead.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=['get'])
    def my_investments(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def update_earnings(self, request):
        total_earned = sync_user_investment_earnings(request.user.profile)
        return Response(
            {'message': 'Earnings updated', 'total_earned': str(total_earned)},
            status=status.HTTP_200_OK,
        )


class PaymentConfirmationViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentConfirmationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentConfirmation.objects.filter(user=self.request.user.profile).select_related(
            'plan',
            'activated_investment',
        ).order_by('-created_at')

    def create(self, request):
        user_profile = request.user.profile
        plan_id = request.data.get('plan_id')
        crypto_type = request.data.get('crypto_type')
        transaction_hash = request.data.get('transaction_hash', '').strip()
        transaction_pin = request.data.get('transaction_pin', '').strip()

        try:
            amount = Decimal(str(request.data.get('amount', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Enter a valid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if user_profile.transaction_pin != transaction_pin:
            return Response({'error': 'Invalid transaction PIN'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            plan = InvestmentPlan.objects.get(id=plan_id, is_active=True)
        except InvestmentPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

        if amount < plan.min_amount or amount > plan.max_amount:
            return Response({'error': 'Amount not within plan range'}, status=status.HTTP_400_BAD_REQUEST)

        if not crypto_type:
            return Response({'error': 'Select the cryptocurrency used for payment'}, status=status.HTTP_400_BAD_REQUEST)

        if not transaction_hash:
            return Response({'error': 'Transaction hash or payment reference is required'}, status=status.HTTP_400_BAD_REQUEST)

        if PaymentConfirmation.objects.filter(transaction_hash__iexact=transaction_hash).exists():
            return Response({'error': 'This transaction hash has already been submitted'}, status=status.HTTP_400_BAD_REQUEST)

        payment = PaymentConfirmation.objects.create(
            user=user_profile,
            plan=plan,
            amount=amount,
            crypto_type=crypto_type,
            transaction_hash=transaction_hash,
        )

        build_activity_log(
            user_profile,
            'payment_pending',
            f'Payment proof submitted for {plan.name}',
            amount=amount,
            plan_name=plan.name,
            status='pending',
            entity_id=payment.id,
            metadata={
                'crypto_type': crypto_type,
                'transaction_hash': transaction_hash,
                'plan_id': str(plan.id),
            },
        )

        return Response(
            {
                'message': 'Payment submitted successfully. Awaiting admin confirmation.',
                'payment_confirmation': PaymentConfirmationSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def my_confirmations(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class WithdrawHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WithdrawHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WithdrawHistory.objects.filter(user=self.request.user.profile).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def my_history(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class CopyTradingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def top_traders(self, request):
        profiles = CopyTradingProfile.objects.filter(is_available=True).select_related('trader__user')
        traders = []
        for profile in profiles:
            traders.append(
                {
                    'id': str(profile.id),
                    'trader_name': profile.trader.user.username,
                    'copy_fee_percentage': profile.copy_fee_percentage,
                    'follower_count': profile.follower_count,
                    'total_copied_value': profile.total_copied_value,
                }
            )
        return Response(traders)

    @action(detail=False, methods=['get'])
    def my_allocations(self, request):
        followers = CopyTradingFollower.objects.filter(
            follower=request.user.profile,
            is_active=True,
        ).select_related('copy_trading_profile__trader__user')
        return Response(CopyTradingFollowerSerializer(followers, many=True).data)

    @action(detail=False, methods=['post'])
    def follow(self, request):
        user_profile = request.user.profile
        profile_id = request.data.get('copy_trading_profile_id')

        try:
            amount = Decimal(str(request.data.get('allocated_amount', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Enter a valid allocation amount'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        if amount > user_profile.balance:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            copy_profile = CopyTradingProfile.objects.get(id=profile_id, is_available=True)
        except CopyTradingProfile.DoesNotExist:
            return Response({'error': 'Trader not found'}, status=status.HTTP_404_NOT_FOUND)

        if CopyTradingFollower.objects.filter(
            follower=user_profile,
            copy_trading_profile=copy_profile,
            is_active=True,
        ).exists():
            return Response({'error': 'Already following this trader'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user_profile.balance -= amount
            user_profile.save(update_fields=['balance', 'updated_at'])

            follower = CopyTradingFollower.objects.create(
                follower=user_profile,
                copy_trading_profile=copy_profile,
                allocated_amount=amount,
            )

            copy_profile.follower_count += 1
            copy_profile.total_copied_value += amount
            copy_profile.save(update_fields=['follower_count', 'total_copied_value'])

            build_activity_log(
                user_profile,
                'copy_trade',
                f'Started copy trading with {copy_profile.trader.user.username}',
                amount=amount,
                status='confirmed',
                entity_id=follower.id,
                metadata={'trader_name': copy_profile.trader.user.username},
            )

        return Response(
            {'message': 'Now copying trader', 'allocation': CopyTradingFollowerSerializer(follower).data},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'])
    def stop(self, request):
        follower_id = request.data.get('follower_id')
        user_profile = request.user.profile

        try:
            follower = CopyTradingFollower.objects.select_related('copy_trading_profile').get(
                id=follower_id,
                follower=user_profile,
                is_active=True,
            )
        except CopyTradingFollower.DoesNotExist:
            return Response({'error': 'Allocation not found'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            follower.is_active = False
            follower.save(update_fields=['is_active'])

            user_profile.balance += follower.allocated_amount
            user_profile.save(update_fields=['balance', 'updated_at'])

            copy_profile = follower.copy_trading_profile
            if copy_profile.follower_count > 0:
                copy_profile.follower_count -= 1
            copy_profile.total_copied_value = max(
                Decimal('0.00'),
                copy_profile.total_copied_value - follower.allocated_amount,
            )
            copy_profile.save(update_fields=['follower_count', 'total_copied_value'])

        return Response({'message': 'Copy trading allocation stopped'}, status=status.HTTP_200_OK)


class CryptoSwapViewSet(viewsets.ModelViewSet):
    serializer_class = CryptoSwapSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CryptoSwap.objects.filter(user=self.request.user.profile).order_by('-created_at')

    def create(self, request):
        user_profile = request.user.profile
        from_crypto = request.data.get('from_crypto')
        to_crypto = request.data.get('to_crypto')

        try:
            from_amount = Decimal(str(request.data.get('from_amount', '0')))
        except (InvalidOperation, TypeError):
            return Response({'error': 'Enter a valid amount'}, status=status.HTTP_400_BAD_REQUEST)

        if not from_crypto or not to_crypto or from_crypto == to_crypto:
            return Response({'error': 'Select two different currencies'}, status=status.HTTP_400_BAD_REQUEST)

        if from_amount <= 0:
            return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        to_amount = from_amount
        fee = (to_amount * Decimal('0.01')).quantize(Decimal('0.01'))
        final_amount = to_amount - fee

        swap = CryptoSwap.objects.create(
            user=user_profile,
            from_crypto=from_crypto,
            to_crypto=to_crypto,
            from_amount=from_amount,
            to_amount=final_amount,
            exchange_rate=Decimal('1.0'),
        )

        build_activity_log(
            user_profile,
            'swap',
            f'Swapped {from_crypto} to {to_crypto}',
            amount=from_amount,
            status='confirmed',
            entity_id=swap.id,
            metadata={'from_crypto': from_crypto, 'to_crypto': to_crypto},
        )

        return Response(
            {
                'message': 'Swap completed',
                'swap': CryptoSwapSerializer(swap).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def my_swaps(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
