# Quick Start Guide - Broker Invest

## 🚀 Fast Setup (5 Minutes)

### Windows

1. **Run Setup Script**
   ```bash
   setup.bat
   ```
   This will automatically:
   - Create virtual environment
   - Install all dependencies
   - Run database migrations
   - Initialize default data

2. **Create Admin User**
   ```bash
   cd backend
   venv\Scripts\activate
   python manage.py createsuperuser
   ```
   Follow prompts to create your admin account

3. **Start the Server**
   ```bash
   python manage.py runserver
   ```

### Mac/Linux

1. **Run Setup Script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Create Admin User**
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py createsuperuser
   ```

3. **Start the Server**
   ```bash
   python manage.py runserver
   ```

## 📱 Accessing the Application

After running the server, open in your browser:

- **Frontend Landing Page**: http://localhost:8000/
- **Login**: http://localhost:8000/login
- **Register**: http://localhost:8000/register
- **Dashboard** (after login): http://localhost:8000/dashboard
- **Django Admin**: http://localhost:8000/backend/admin/
- **API Endpoints**: http://localhost:8000/api/

## 🔑 Default Admin Credentials (Custom Admin)

For the custom admin backend (NOT Django admin):
- **Email**: Vera@admin.com
- **Password**: AdminVera

## 📊 Investment Plans

The following plans are automatically created:

| Plan | Daily % | Min | Max | Duration |
|------|---------|-----|-----|----------|
| Starter | 3.5% | $10 | $1,000 | 30 days |
| Professional | 5% | $1,000 | $10,000 | 30 days |
| Premium | 7.5% | $5,000 | $50,000 | 30 days |
| Elite | 10% | $25,000 | Unlimited | 30 days |
| VIP | 15% | $50,000 | Unlimited | 60 days |

## 🔐 Test Account Creation

1. Go to http://localhost:8000/register
2. Create test account:
   - Username: `testuser`
   - Password: `TestPassword123`
   - Transaction PIN: `1234`
   - Referral Code: (leave empty)

3. Login with created credentials
4. Access your dashboard

## 💰 Making a Test Investment

1. Login to dashboard
2. Click "Investments" in sidebar
3. Choose a plan
4. Enter amount within plan limits
5. Enter your transaction PIN
6. Click "Invest Now"
7. View in dashboard

## 💳 Test Withdrawal

1. In dashboard, go to "Withdraw"
2. Select withdrawal method:
   - **Crypto**: Choose BTC/ETH/USDT
   - **Bank**: Select bank transfer
3. Enter amount
4. For crypto, wallet address is pre-filled
5. Submit request
6. See "Processing" modal (10-30 min message)

## 🤝 Referral Program

1. Go to "Refer & Earn"
2. Copy your unique referral code
3. Share with others
4. When they register with your code, you earn 10% from their investments

## 📬 Telegram Notifications Setup

To enable Telegram alerts:

1. **Create Telegram Bot**
   - Open Telegram
   - Find @BotFather
   - Send `/start` then `/newbot`
   - Follow instructions, get bot token

2. **Get Your Chat ID**
   - Message your new bot
   - Send `/start`
   - Use @userinfobot to get your chat ID

3. **Update Configuration**
   - Edit `backend/.env`
   - Add:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     TELEGRAM_ADMIN_CHAT_ID=your_chat_id_here
     ```

4. **Restart Server**
   - Stop: Ctrl+C
   - Start: `python manage.py runserver`

## 🎨 Adding Images

See **IMAGES_GUIDE.md** for detailed instructions.

Quick images to add:
1. Logo: `frontend/static/images/logo.png`
2. Hero image: `frontend/static/images/hero.jpg`
3. Icons: `frontend/static/images/icons/`
4. Crypto icons: `frontend/static/images/crypto/`

## 🗄️ Database Management

### Check Database Status
```bash
python manage.py migrate --list
```

### Reset Database (Careful!)
```bash
# Delete sqlite database
rm db.sqlite3

# Recreate migrations and data
python manage.py makemigrations
python manage.py migrate
python init_data.py
```

### Create Backup
```bash
# Copy db.sqlite3 to safe location
cp db.sqlite3 db.sqlite3.backup
```

## 🛠️ Troubleshooting

### Issue: Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001
```

### Issue: Module not found
```bash
# Activate virtual environment first
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### Issue: Database locked
```bash
# Delete sqlite database and restart
rm backend/db.sqlite3
python manage.py migrate
python manage.py runserver
```

### Issue: CORS errors
Already configured! Update in `broker_core/settings.py` if needed:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

## 📚 API Testing with Curl

### Register User
```bash
curl -X POST http://localhost:8000/api/users/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "transaction_pin": "1234"
  }'
```

### Get Investment Plans
```bash
curl http://localhost:8000/api/investments/plans/
```

### Get User Investments (need auth)
```bash
curl -H "Authorization: Bearer <user_id>" \
  http://localhost:8000/api/investments/active/my_investments/
```

## 🔄 Background Tasks (Optional)

To enable automatic earnings calculation (requires Celery & Redis):

1. **Install Redis**:
   - Windows: Download from `https://github.com/microsoftarchive/redis/releases`
   - Mac: `brew install redis`
   - Linux: `sudo apt-get install redis-server`

2. **Start Redis**: `redis-server`

3. **Start Celery Worker**:
   ```bash
   celery -A broker_core worker -l info
   ```

## 📈 Scaling to Production

1. **Use PostgreSQL** instead of SQLite
2. **Deploy on**: Heroku, DigitalOcean, AWS
3. **Use Gunicorn**: `gunicorn broker_core.wsgi`
4. **Enable HTTPS**: Let's Encrypt SSL
5. **Use Nginx**: Reverse proxy
6. **Use Redis**: Caching and Celery

## 📞 Support

- **Documentation**: README.md
- **Images Guide**: IMAGES_GUIDE.md
- **API Docs**: See API Endpoints section
- **Issues**: Check logs in terminal

## ✅ Checklist

- [ ] Setup script ran successfully
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Database migrations completed
- [ ] Data initialized (plans created)
- [ ] Server running on port 8000
- [ ] Can access http://localhost:8000
- [ ] Can register new account
- [ ] Can login to dashboard
- [ ] Can create investment
- [ ] Can request withdrawal
- [ ] Telegram (optional) configured

## 🎉 You're Ready!

Your Broker Invest platform is now running!

Next steps:
1. Customize site settings (admin panel)
2. Add payment wallet addresses
3. Add images to make it beautiful
4. Test all features
5. Deploy to production

Happy investing! 🚀

---

**Questions?** Check the README.md for detailed documentation.
