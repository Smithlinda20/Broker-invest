import requests
from django.conf import settings
from admin_panel.models import AdminNotification, PopupNotification, SiteSettings


def _is_placeholder(value):
    return not value or str(value).startswith('YOUR_')


def send_telegram_notification(message):
    """Send notification to admin via Telegram"""
    try:
        settings_obj = SiteSettings.objects.first()
        if (
            not settings_obj
            or _is_placeholder(settings_obj.telegram_bot_token)
            or _is_placeholder(settings_obj.telegram_admin_chat_id)
        ):
            return False
        
        url = f"https://api.telegram.org/bot{settings_obj.telegram_bot_token}/sendMessage"
        data = {
            'chat_id': settings_obj.telegram_admin_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram notification error: {str(e)}")
        return False

def create_investment_alert(user_profile, investment):
    """Create alert for investment"""
    message = f"🔔 <b>New Investment</b>\n\n" \
              f"👤 User: <b>{user_profile.user.username}</b>\n" \
              f"💰 Amount: <b>${investment.amount}</b>\n" \
              f"📦 Package: <b>{investment.plan.name}</b>\n" \
              f"📈 Daily Return: <b>{investment.plan.daily_return_percentage}%</b>"
    
    # Send Telegram alert
    send_telegram_notification(message)
    
    # Create admin notification
    AdminNotification.objects.create(
        alert_type='investment',
        username=user_profile.user.username,
        message=message,
        amount=investment.amount,
        package_name=investment.plan.name
    )

def create_withdrawal_alert(withdrawal):
    """Create alert for withdrawal"""
    crypto_text = f" ({withdrawal.crypto_type})" if withdrawal.crypto_type else ""
    message = f"💸 <b>Withdrawal Request</b>\n\n" \
              f"👤 User: <b>{withdrawal.user.user.username}</b>\n" \
              f"💰 Amount: <b>${withdrawal.amount}</b>\n" \
              f"🔄 Method: <b>{withdrawal.method.upper()}{crypto_text}</b>\n" \
              f"⏳ Status: <b>Pending</b>"
    
    # Send Telegram alert
    send_telegram_notification(message)
    
    # Create admin notification
    AdminNotification.objects.create(
        alert_type='withdrawal',
        username=withdrawal.user.user.username,
        message=message,
        amount=withdrawal.amount
    )
    
    # Create popup notification
    PopupNotification.objects.create(
        username=withdrawal.user.user.username,
        amount=withdrawal.amount
    )

def create_referral_alert(referrer, referred_user, amount):
    """Create alert for referral earning"""
    message = f"🎁 <b>Referral Earning</b>\n\n" \
              f"👤 Referrer: <b>{referrer.user.username}</b>\n" \
              f"👥 Referred: <b>{referred_user.user.username}</b>\n" \
              f"💰 Earning: <b>${amount}</b>"
    
    AdminNotification.objects.create(
        alert_type='referral',
        username=referrer.user.username,
        message=message,
        amount=amount
    )
