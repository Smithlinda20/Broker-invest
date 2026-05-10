from django.contrib import admin
from .models import AdminNotification, PaymentWallet, SiteSettings, PopupNotification

@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'username', 'amount', 'is_read', 'created_at']
    list_filter = ['alert_type', 'is_read', 'created_at']
    search_fields = ['username', 'message']

@admin.register(PaymentWallet)
class PaymentWalletAdmin(admin.ModelAdmin):
    list_display = ['crypto_type', 'network', 'is_active', 'created_at']

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'support_email', 'updated_at']

@admin.register(PopupNotification)
class PopupNotificationAdmin(admin.ModelAdmin):
    list_display = ['username', 'amount', 'created_at']
