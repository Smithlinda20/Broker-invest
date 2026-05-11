import os
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_core.settings')
django.setup()

from investments.models import InvestmentPlan
from admin_panel.models import SiteSettings, PaymentWallet

# Create Investment Plans
print("Creating investment plans...")
plans_data = [
    {
        'name': 'Starter Plan',
        'min_amount': 100,
        'max_amount': 1000,
        'daily_return_percentage': 3.5,
        'duration_days': 30,
        'description': 'Perfect for beginners with guaranteed daily returns'
    },
    {
        'name': 'Professional Plan',
        'min_amount': 1000,
        'max_amount': 10000,
        'daily_return_percentage': 5,
        'duration_days': 30,
        'description': 'For serious investors looking for consistent returns'
    },
    {
        'name': 'Premium Plan',
        'min_amount': 5000,
        'max_amount': 50000,
        'daily_return_percentage': 7.5,
        'duration_days': 30,
        'description': 'Premium package with higher daily returns'
    },
    {
        'name': 'Elite Plan',
        'min_amount': 25000,
        'max_amount': 999999999.99,
        'daily_return_percentage': 10,
        'duration_days': 30,
        'description': 'Elite investment plan for high rollers'
    },
    {
        'name': 'VIP Plan',
        'min_amount': 50000,
        'max_amount': 999999999.99,
        'daily_return_percentage': 15,
        'duration_days': 60,
        'description': 'VIP exclusive plan with maximum returns'
    }
]

for plan_data in plans_data:
    plan, created = InvestmentPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults=plan_data
    )
    if created:
        print(f"✓ Created {plan.name}")
    else:
        print(f"⊘ {plan.name} already exists")

# Create Site Settings
print("\nCreating site settings...")
settings, created = SiteSettings.objects.get_or_create(
    id='00000000-0000-0000-0000-000000000001',
    defaults={
        'company_name': 'Broker Invest',
        'support_email': 'support@brokerinvest.com',
        'support_phone': '+1-800-000-0000',
        'support_address': '123 Business Street, Financial District, New York, NY 10001',
        'footer_text': '© 2024 Broker Invest. All rights reserved. | Secure Investment Platform',
        'telegram_bot_token': 'YOUR_TELEGRAM_BOT_TOKEN',
        'telegram_admin_chat_id': 'YOUR_TELEGRAM_CHAT_ID'
    }
)
if created:
    print("✓ Site settings created")
else:
    print("⊘ Site settings already exist")

# Create Payment Wallets
print("\nCreating payment wallets...")
wallets_data = [
    {
        'crypto_type': 'BTC',
        'wallet_address': 'bc1q4wx55uqrcc23ymrzk6q5n0lvhgxpzwnmnnqtnr',
        'network': 'Bitcoin Mainnet',
        'logo_url': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons/32/color/btc.png',
        'qr_code': '/static/images/Qr.jpg',
        'is_active': True
    },
    {
        'crypto_type': 'ETH',
        'wallet_address': '0xBd03DB12f117Af1529030DDbcc72Dd4E5E462220',
        'network': 'Ethereum Mainnet',
        'logo_url': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons/32/color/eth.png',
        'qr_code': '',
        'is_active': True
    },
    {
        'crypto_type': 'USDT',
        'wallet_address': '0xBd03DB12f117Af1529030DDbcc72Dd4E5E462220',
        'network': 'Ethereum (ERC-20)',
        'logo_url': 'https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons/32/color/usdt.png',
        'qr_code': '',
        'is_active': True
    }
]

for wallet_data in wallets_data:
    wallet, created = PaymentWallet.objects.get_or_create(
        crypto_type=wallet_data['crypto_type'],
        defaults=wallet_data
    )
    if created:
        print(f"✓ Created {wallet.crypto_type} wallet")
    else:
        print(f"⊘ {wallet.crypto_type} wallet already exists")

print("\n✅ Database initialization complete!")
print("\nReminder: Update Telegram credentials in site settings for alerts to work.")



from django.contrib.auth.hashers import make_password
from admin_panel.models import AdminUser

# Create default admin user
admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
admin_name = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'Admin')

if admin_email and admin_password:
    if not AdminUser.objects.filter(email=admin_email).exists():
        AdminUser.objects.create(
            email=admin_email,
            password=make_password(admin_password),
            name=admin_name,
            is_active=True
        )
        print(f"✅ Admin user created: {admin_email}")
    else:
        print(f"⊘ Admin user already exists: {admin_email}")
