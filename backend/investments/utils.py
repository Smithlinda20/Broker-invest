from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import ActiveInvestment


def sync_user_investment_earnings(user_profile):
    total_earned = Decimal('0.00')
    active_investments = ActiveInvestment.objects.filter(
        user=user_profile,
        status='active',
    ).select_related('plan')

    with transaction.atomic():
        for investment in active_investments:
            earned = investment.calculate_earnings()
            if earned:
                total_earned += earned

        if total_earned:
            user_profile.balance += total_earned
            user_profile.save(update_fields=['balance', 'updated_at'])

    ActiveInvestment.objects.filter(
        user=user_profile,
        status='active',
        end_date__lte=timezone.now(),
    ).update(status='completed')

    return total_earned
