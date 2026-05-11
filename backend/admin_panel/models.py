from django.db import models
import uuid

class AdminNotification(models.Model):
    ALERT_TYPES = [
        ('investment', 'Investment'),
        ('withdrawal', 'Withdrawal'),
        ('referral', 'Referral'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    username = models.CharField(max_length=150)
    message = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    package_name = models.CharField(max_length=100, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.username}"

class PaymentWallet(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'USDT'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crypto_type = models.CharField(max_length=10, choices=CRYPTO_CHOICES, unique=True)
    wallet_address = models.CharField(max_length=255)
    network = models.CharField(max_length=100)
    logo_url = models.CharField(max_length=500, blank=True, null=True)
    qr_code = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.crypto_type} - {self.network}"

class SiteSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=200)
    support_email = models.EmailField()
    support_phone = models.CharField(max_length=20)
    support_address = models.TextField()

    footer_text = models.TextField()
    telegram_bot_token = models.CharField(max_length=255)
    telegram_admin_chat_id = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return self.company_name

class PopupNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} withdrew {self.amount}"


class AdminUser(models.Model):
    """Custom Admin User Model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Should be hashed
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class ActivityLog(models.Model):
    """Track all user activities"""
    ACTIVITY_TYPES = [
        ('registration', 'User Registration'),
        ('login', 'User Login'),
        ('investment', 'Investment Created'),
        ('payment_pending', 'Payment Pending'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('payment_rejected', 'Payment Rejected'),
        ('withdrawal_requested', 'Withdrawal Requested'),
        ('withdrawal_processed', 'Withdrawal Processed'),
        ('referral', 'Referral Reward'),
        ('copy_trade', 'Copy Trading Started'),
        ('swap', 'Crypto Swap'),
        ('wallet_import', 'Wallet Imported'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.CharField(max_length=255)
    username = models.CharField(max_length=150)
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')  # pending, confirmed, rejected, processed
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_email']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.get_activity_type_display()}"

