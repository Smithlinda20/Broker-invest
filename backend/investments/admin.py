from django.contrib import admin
from .models import InvestmentPlan, ActiveInvestment, WithdrawHistory

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'daily_return_percentage', 'min_amount', 'max_amount']

@admin.register(ActiveInvestment)
class ActiveInvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'earned', 'status']

@admin.register(WithdrawHistory)
class WithdrawHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'created_at']
