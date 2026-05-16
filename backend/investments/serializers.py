from rest_framework import serializers
from .models import (
    ActiveInvestment,
    CopyTradingFollower,
    CryptoSwap,
    InvestmentPlan,
    PaymentConfirmation,
    WithdrawHistory,
)

class InvestmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPlan
        fields = ['id', 'name', 'min_amount', 'max_amount', 'daily_return_percentage', 'duration_days', 'description']

class ActiveInvestmentSerializer(serializers.ModelSerializer):
    plan = InvestmentPlanSerializer(read_only=True)
    username = serializers.CharField(source='user.user.username', read_only=True)
    
    class Meta:
        model = ActiveInvestment
        fields = ['id', 'user', 'username', 'plan', 'amount', 'earned', 'status', 'start_date', 'end_date']
        read_only_fields = fields

class WithdrawHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawHistory
        fields = ['id', 'user', 'amount', 'investment', 'created_at']
        read_only_fields = fields


class PaymentConfirmationSerializer(serializers.ModelSerializer):
    plan = InvestmentPlanSerializer(read_only=True)
    username = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = PaymentConfirmation
        fields = [
            'id',
            'user',
            'username',
            'plan',
            'amount',
            'crypto_type',
            'transaction_hash',
            'status',
            'created_at',
            'confirmed_at',
            'activated_investment',
        ]
        read_only_fields = fields


class CopyTradingFollowerSerializer(serializers.ModelSerializer):
    trader_name = serializers.CharField(source='copy_trading_profile.trader.user.username', read_only=True)
    fee_percentage = serializers.DecimalField(
        source='copy_trading_profile.copy_fee_percentage',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CopyTradingFollower
        fields = [
            'id',
            'allocated_amount',
            'is_active',
            'created_at',
            'trader_name',
            'fee_percentage',
        ]
        read_only_fields = fields


class CryptoSwapSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoSwap
        fields = [
            'id',
            'from_crypto',
            'to_crypto',
            'from_amount',
            'to_amount',
            'exchange_rate',
            'fee_percentage',
            'status',
            'created_at',
        ]
        read_only_fields = fields
