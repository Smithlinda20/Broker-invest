from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    transaction_pin = models.CharField(max_length=4)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=20, unique=True)
    referral_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username

class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    method = models.CharField(max_length=20, choices=[('crypto', 'Crypto'), ('bank', 'Bank Transfer')])
    crypto_type = models.CharField(max_length=10, null=True, blank=True, choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT', 'USDT')])
    bank_details = models.JSONField(null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.amount}"

class ReferralEarning(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='referral_earnings_made')
    referred_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='referred_from')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.user.username} -> {self.referred_user.user.username}"

class ImportedWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='imported_wallets')
    wallet_address = models.CharField(max_length=255)
    wallet_type = models.CharField(max_length=20, choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT', 'USDT')])
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.wallet_type}"
