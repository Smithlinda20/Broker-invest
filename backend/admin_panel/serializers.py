from rest_framework import serializers
from .models import AdminNotification, PaymentWallet, SiteSettings, PopupNotification

class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = ['id', 'alert_type', 'username', 'message', 'amount', 'package_name', 'is_read', 'created_at']

class PaymentWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentWallet
        fields = ['id', 'crypto_type', 'wallet_address', 'network', 'is_active']

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['company_name', 'support_email', 'support_phone', 'support_address', 'footer_text']

class PopupNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopupNotification
        fields = ['id', 'username', 'amount', 'created_at']
