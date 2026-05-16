from datetime import timedelta
from decimal import Decimal
import uuid

from django.db import models
from django.utils import timezone

from users.models import UserProfile

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
        """Accrue earnings in exact 24-hour intervals without overpaying past plan end."""
        now = timezone.now()
        last_update = self.last_earning_update or self.start_date
        effective_now = min(now, self.end_date)

        if effective_now <= last_update:
            if now >= self.end_date and self.status == 'active':
                self.status = 'completed'
                self.save(update_fields=['status'])
            return Decimal('0.00')

        completed_periods = int((effective_now - last_update) // timedelta(hours=24))
        if completed_periods <= 0:
            if now >= self.end_date and self.status == 'active':
                self.status = 'completed'
                self.save(update_fields=['status'])
            return Decimal('0.00')

        daily_return = self.amount * (self.plan.daily_return_percentage / Decimal('100'))
        new_earnings = daily_return * completed_periods
        self.earned += new_earnings
        self.last_earning_update = last_update + (timedelta(hours=24) * completed_periods)

        if now >= self.end_date and self.status == 'active':
            self.status = 'completed'

        self.save(update_fields=['earned', 'last_earning_update', 'status'])
        return new_earnings

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
    activated_investment = models.OneToOneField(
        ActiveInvestment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payment_confirmation',
    )
    
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
