from rest_framework import serializers
from .models import InvestmentPlan, ActiveInvestment, WithdrawHistory

class InvestmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPlan
        fields = ['id', 'name', 'min_amount', 'max_amount', 'daily_return_percentage', 'duration_days', 'description']

class ActiveInvestmentSerializer(serializers.ModelSerializer):
    plan = InvestmentPlanSerializer()
    
    class Meta:
        model = ActiveInvestment
        fields = ['id', 'user', 'plan', 'amount', 'earned', 'status', 'start_date', 'end_date']

class WithdrawHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawHistory
        fields = ['id', 'user', 'amount', 'investment', 'created_at']
