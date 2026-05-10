from django.db.models.signals import post_save
from django.dispatch import receiver
from investments.models import ActiveInvestment
from users.models import Withdrawal
from notifications.utils import create_investment_alert, create_withdrawal_alert

@receiver(post_save, sender=ActiveInvestment)
def investment_created_signal(sender, instance, created, **kwargs):
    """Signal when investment is created"""
    if created:
        create_investment_alert(instance.user, instance)

@receiver(post_save, sender=Withdrawal)
def withdrawal_created_signal(sender, instance, created, **kwargs):
    """Signal when withdrawal is created"""
    if created:
        create_withdrawal_alert(instance)
