from django.contrib import admin
from .models import UserProfile, Withdrawal, ReferralEarning

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'referral_code', 'created_at']

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created_at']

@admin.register(ReferralEarning)
class ReferralEarningAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred_user', 'amount', 'created_at']
