# Broker Invest - Premium Investment Platform

A full-stack investment platform built with Django and modern frontend technologies. Features investment plans with daily returns, user authentication, withdrawal system, referral program, and admin dashboard with Telegram alerts.

## Features

✨ **Investment Plans** - 5 different plans with returns from 3.5% to 15% daily
💰 **Secure Withdrawals** - Multiple withdrawal methods (Crypto & Bank Transfer)
👥 **Referral Program** - Earn 10% commission from referrals
🔔 **Real-time Alerts** - Telegram notifications for admin on investments and withdrawals
📊 **Admin Dashboard** - Manage payments, settings, and view all transactions
🎨 **Modern UI** - Beautiful, responsive design inspired by leading crypto platforms

## Project Structure

```
Broker-invest/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── broker_core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── investments/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── admin_panel/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── payments/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── notifications/
│   │   ├── utils.py
│   │   ├── signals.py
│   │   └── models.py
│   └── staticfiles/
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   └── dashboard.js
│   │   └── images/
│   └── templates/
│       ├── index.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── dashboard/
│           └── dashboard.html
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual Environment

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create a `.env` file in the backend directory:
```
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-telegram-chat-id
```

4. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser (for Django Admin)**
```bash
python manage.py createsuperuser
```

**Admin Credentials for Custom Admin:**
- Email: `Vera@admin.com`
- Password: `AdminVera`

6. **Create Investment Plans**
```bash
python manage.py shell
```

Then in the Django shell:
```python
from investments.models import InvestmentPlan

plans = [
    {
        'name': 'Starter Plan',
        'min_amount': 10,
        'max_amount': 1000,
        'daily_return_percentage': 3.5,
        'duration_days': 30,
        'description': 'Perfect for beginners'
    },
    {
        'name': 'Professional Plan',
        'min_amount': 1000,
        'max_amount': 10000,
        'daily_return_percentage': 5,
        'duration_days': 30,
        'description': 'For serious investors'
    },
    {
        'name': 'Premium Plan',
        'min_amount': 5000,
        'max_amount': 50000,
        'daily_return_percentage': 7.5,
        'duration_days': 30,
        'description': 'Premium returns'
    },
    {
        'name': 'Elite Plan',
        'min_amount': 25000,
        'max_amount': 999999999.99,
        'daily_return_percentage': 10,
        'duration_days': 30,
        'description': 'Elite investment plan'
    },
    {
        'name': 'VIP Plan',
        'min_amount': 50000,
        'max_amount': 999999999.99,
        'daily_return_percentage': 15,
        'duration_days': 60,
        'description': 'VIP exclusive plan'
    }
]

for plan_data in plans:
    InvestmentPlan.objects.create(**plan_data)

print("Plans created successfully!")
exit()
```

7. **Create Admin Settings**
```python
from admin_panel.models import SiteSettings

SiteSettings.objects.create(
    company_name='Broker Invest',
    support_email='support@brokerinvest.com',
    support_phone='+1-800-000-0000',
    support_address='123 Business St, City, Country',
    footer_text='© 2024 Broker Invest. All rights reserved.',
    telegram_bot_token='your-telegram-bot-token',
    telegram_admin_chat_id='your-telegram-chat-id'
)
exit()
```

8. **Add Payment Wallets**
```python
from admin_panel.models import PaymentWallet

wallets = [
    {
        'crypto_type': 'BTC',
        'wallet_address': 'your-bitcoin-address',
        'network': 'Bitcoin Mainnet'
    },
    {
        'crypto_type': 'ETH',
        'wallet_address': 'your-ethereum-address',
        'network': 'Ethereum Mainnet'
    },
    {
        'crypto_type': 'USDT',
        'wallet_address': 'your-usdt-address',
        'network': 'Ethereum (ERC-20)'
    }
]

for wallet_data in wallets:
    PaymentWallet.objects.create(**wallet_data)

exit()
```

### Frontend Setup

The frontend files are already in place:
- Landing page: `frontend/templates/index.html`
- Authentication pages: `frontend/templates/auth/`
- Dashboard: `frontend/templates/dashboard/dashboard.html`
- Styles: `frontend/static/css/style.css`
- Scripts: `frontend/static/js/`

### Running the Application

1. **Start Django Server**
```bash
cd backend
python manage.py runserver
```

The backend will run on `http://localhost:8000`

2. **Access the Application**
- Frontend: `http://localhost:8000` (or serve via separate web server)
- Admin Django: `http://localhost:8000/backend/admin/`
- API: `http://localhost:8000/api/`

## API Endpoints

### Users
- `POST /api/users/users/register/` - Register new user
- `POST /api/users/users/login/` - Login user
- `GET /api/users/withdrawals/history/` - Get withdrawal history
- `POST /api/users/withdrawals/` - Request withdrawal

### Investments
- `GET /api/investments/plans/` - Get all investment plans
- `GET /api/investments/active/my_investments/` - Get user's active investments
- `POST /api/investments/active/` - Create new investment

### Admin
- `GET /api/admin/notifications/` - Get admin notifications
- `POST /api/admin/notifications/mark_all_as_read/` - Mark all notifications as read
- `GET /api/admin/payment-wallets/` - Get payment wallet addresses
- `POST /api/admin/payment-wallets/` - Create payment wallet
- `GET /api/admin/settings/get_settings/` - Get site settings
- `POST /api/admin/settings/` - Update site settings

## How Alerts Work

### Investment Alert
When a user creates an investment:
1. Alert is sent to admin via Telegram
2. Admin notification is stored in database
3. User sees confirmation on dashboard

### Withdrawal Alert
When a user requests a withdrawal:
1. Alert is sent to admin via Telegram
2. Admin notification is stored in database
3. Popup notification is created for other users
4. User sees processing modal with "10-30 minutes" message

### Random Popup Notifications
- Every 15-20 seconds, a random recent withdrawal is shown as a popup
- Shows username and amount withdrawn
- Helps create social proof and engagement

## Admin Panel

Access admin panel at `/backend/admin/login` with credentials:
- Email: `Vera@admin.com`
- Password: `AdminVera`

### Admin Features
- View all investment/withdrawal alerts
- Manage payment wallet addresses and networks
- Edit site settings (footer, contact info, etc.)
- View user profiles and transactions
- Manage investment plans

## Telegram Integration

To enable Telegram alerts:

1. **Create Telegram Bot**
   - Message @BotFather on Telegram
   - Create new bot and get the token

2. **Get Chat ID**
   - Message your bot with `/start`
   - Send message: `@userinfobot` to get your chat ID

3. **Update .env**
```
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
```

## Adding Images

To add professional images:

1. Download images from:
   - `unsplash.com` - Finance/Crypto images
   - `pexels.com` - Professional business images
   - `pixabay.com` - Investment/Trading images

2. Save images to `frontend/static/images/`

3. Update HTML to use images:
```html
<img src="/static/images/investment-hero.jpg" alt="Investment">
```

## Deployment

### For Production:
1. Set `DEBUG=False` in settings.py
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL recommended)
4. Use Gunicorn or similar WSGI server
5. Set up SSL certificate
6. Use environment variables for sensitive data

```bash
gunicorn broker_core.wsgi:application --bind 0.0.0.0:8000
```

## Database Models

### UserProfile
- Extends Django User model
- Stores transaction PIN, balance, referral code
- Tracks referral earnings

### ActiveInvestment
- Links user to investment plan
- Tracks invested amount and daily earnings
- Automatically calculates returns

### Withdrawal
- Stores withdrawal requests
- Supports crypto and bank transfer methods
- Tracks status (pending, approved, rejected)

### AdminNotification
- Stores all alerts (investments, withdrawals, referrals)
- Used for admin dashboard

### PaymentWallet
- Stores cryptocurrency wallet addresses
- Includes network information for user reference

### SiteSettings
- Centralized configuration
- Support contact information
- Telegram bot configuration

## Security Features

✅ Password validation
✅ Transaction PIN requirement
✅ CORS protection
✅ SQL injection prevention (ORM)
✅ CSRF token protection
✅ Secure session management
✅ Environment variable encryption

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Packages won't install
```bash
pip install --default-timeout=1000 -r requirements.txt
```

### Django migrations error
```bash
python manage.py makemigrations --empty yourappname --name some_name
python manage.py migrate
```

### CORS errors
Update CORS settings in `broker_core/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://your-domain.com",
]
```

## Support & Contact

For issues or questions:
- Email: support@brokerinvest.com
- Phone: +1-800-000-0000
- Address: 123 Business St, City, Country

## License

This project is proprietary and confidential.

## Changelog

### v1.0.0 (Initial Release)
- Complete investment platform
- 5 investment plans
- User authentication
- Cryptocurrency and bank withdrawals
- Referral program
- Admin dashboard with Telegram alerts
- Responsive design

---

**Made with ❤️ by Broker Invest Team**
