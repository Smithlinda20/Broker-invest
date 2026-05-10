from django.db import models
from users.models import UserProfile
import uuid
from datetime import datetime, timedelta

class InvestmentPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=15, decimal_places=2)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    daily_return_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.IntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.daily_return_percentage}%"

class ActiveInvestment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='investments')
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    last_earning_update = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.plan.name}"
    
    def calculate_earnings(self):
        """Calculate daily earnings"""
        now = datetime.now()
        last_update = self.last_earning_update
        
        if (now - last_update).days >= 1:
            days_passed = (now - last_update).days
            daily_return = self.amount * (self.plan.daily_return_percentage / 100)
            new_earnings = daily_return * days_passed
            self.earned += new_earnings
            self.last_earning_update = now
            self.save()
            return new_earnings
        return 0

class WithdrawHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='withdraw_history')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    investment = models.ForeignKey(ActiveInvestment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentConfirmation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payment_confirmations')
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    crypto_type = models.CharField(max_length=20)
    transaction_hash = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.status}"

class CopyTradingProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trader = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='copy_trading_profile')
    is_available = models.BooleanField(default=False)
    copy_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    follower_count = models.IntegerField(default=0)
    total_copied_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.trader.user.username} - Copy Trading"

class CopyTradingFollower(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='followed_traders')
    copy_trading_profile = models.ForeignKey(CopyTradingProfile, on_delete=models.CASCADE, related_name='followers')
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.follower.user.username} following {self.copy_trading_profile.trader.user.username}"

class CryptoSwap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='crypto_swaps')
    from_crypto = models.CharField(max_length=20)
    to_crypto = models.CharField(max_length=20)
    from_amount = models.DecimalField(max_digits=15, decimal_places=2)
    to_amount = models.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=8)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    status = models.CharField(max_length=20, default='completed', choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.from_crypto} to {self.to_crypto}"
    
    def __str__(self):
        return f"{self.user.user.username} - {self.amount}"
