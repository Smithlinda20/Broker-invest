# API Documentation - Broker Invest

## Base URL
```
http://localhost:8000/api
```

## Authentication
Most endpoints require authentication. Use your user ID as the bearer token:
```
Authorization: Bearer <user_id>
```

---

## 📝 User Endpoints

### Register User
**POST** `/users/users/register/`

Request:
```json
{
  "username": "john_doe",
  "password": "secure_password",
  "transaction_pin": "1234",
  "referral_code": "ABC123XYZ"  // optional
}
```

Response:
```json
{
  "message": "User registered successfully",
  "user_id": "uuid",
  "referral_code": "GH56IJKL"
}
```

### Login User
**POST** `/users/users/login/`

Request:
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

Response:
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "profile": {
    "id": "uuid",
    "balance": 1000.00,
    "referral_code": "GH56IJKL",
    "referral_earnings": 50.00,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Withdrawal History
**GET** `/users/withdrawals/history/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
[
  {
    "id": "uuid",
    "user": "uuid",
    "amount": 100.00,
    "method": "crypto",
    "crypto_type": "BTC",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Request Withdrawal
**POST** `/users/withdrawals/`

Headers:
```
Authorization: Bearer <user_id>
Content-Type: application/json
```

Request (Crypto):
```json
{
  "amount": 100.00,
  "method": "crypto",
  "crypto_type": "BTC",
  "wallet_address": "1A1z7agoat5P5EQYLskRQprUtRAG5sDRA"
}
```

Request (Bank):
```json
{
  "amount": 100.00,
  "method": "bank",
  "bank_details": {
    "account_number": "1234567890",
    "bank_name": "Example Bank"
  }
}
```

Response:
```json
{
  "message": "Withdrawal request submitted. Processing within 10-30 minutes",
  "withdrawal": {
    "id": "uuid",
    "amount": 100.00,
    "method": "crypto",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Referrals
**GET** `/users/referrals/my_referrals/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
[
  {
    "id": "uuid",
    "referrer": "uuid",
    "referred_user": "uuid",
    "amount": 50.00,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## 💰 Investment Endpoints

### Get All Investment Plans
**GET** `/investments/plans/`

No authentication required.

Response:
```json
[
  {
    "id": "uuid",
    "name": "Starter Plan",
    "min_amount": 10.00,
    "max_amount": 1000.00,
    "daily_return_percentage": 3.50,
    "duration_days": 30,
    "description": "Perfect for beginners"
  },
  {
    "id": "uuid",
    "name": "Professional Plan",
    "min_amount": 1000.00,
    "max_amount": 10000.00,
    "daily_return_percentage": 5.00,
    "duration_days": 30,
    "description": "For serious investors"
  }
]
```

### Create Investment
**POST** `/investments/active/`

Headers:
```
Authorization: Bearer <user_id>
Content-Type: application/json
```

Request:
```json
{
  "plan_id": "plan_uuid",
  "amount": 500.00
}
```

Response:
```json
{
  "message": "Investment created successfully",
  "investment": {
    "id": "uuid",
    "user": "uuid",
    "plan": {
      "id": "uuid",
      "name": "Professional Plan",
      "daily_return_percentage": 5.00
    },
    "amount": 500.00,
    "earned": 0.00,
    "status": "active",
    "start_date": "2024-01-15T10:30:00Z",
    "end_date": "2024-02-14T10:30:00Z"
  }
}
```

### Get User Investments
**GET** `/investments/active/my_investments/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
[
  {
    "id": "uuid",
    "user": "uuid",
    "plan": { /* plan details */ },
    "amount": 500.00,
    "earned": 75.00,
    "status": "active",
    "start_date": "2024-01-15T10:30:00Z",
    "end_date": "2024-02-14T10:30:00Z"
  }
]
```

### Update Earnings
**GET** `/investments/active/update_earnings/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
{
  "message": "Earnings updated",
  "total_earned": 25.00
}
```

### Get Withdrawal History
**GET** `/investments/history/my_history/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
[
  {
    "id": "uuid",
    "user": "uuid",
    "amount": 50.00,
    "investment": "uuid",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## 🔔 Admin Endpoints

### Get Notifications
**GET** `/admin/notifications/`

Headers:
```
Authorization: Bearer <user_id>
```
(Requires admin privileges)

Response:
```json
[
  {
    "id": "uuid",
    "alert_type": "investment",
    "username": "john_doe",
    "message": "User invested $500 in Professional Plan",
    "amount": 500.00,
    "package_name": "Professional Plan",
    "is_read": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Mark Notification as Read
**POST** `/admin/notifications/{id}/mark_as_read/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
{
  "status": "notification marked as read"
}
```

### Mark All Notifications as Read
**POST** `/admin/notifications/mark_all_as_read/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
{
  "status": "all notifications marked as read"
}
```

### Get Unread Count
**GET** `/admin/notifications/unread_count/`

Headers:
```
Authorization: Bearer <user_id>
```

Response:
```json
{
  "unread_count": 5
}
```

### Get Payment Wallets
**GET** `/admin/payment-wallets/`

No authentication required.

Response:
```json
[
  {
    "id": "uuid",
    "crypto_type": "BTC",
    "wallet_address": "1A1z7agoat5P5EQYLskRQprUtRAG5sDRA",
    "network": "Bitcoin Mainnet",
    "is_active": true
  },
  {
    "id": "uuid",
    "crypto_type": "ETH",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f1bEb",
    "network": "Ethereum Mainnet",
    "is_active": true
  }
]
```

### Create Payment Wallet
**POST** `/admin/payment-wallets/`

Headers:
```
Authorization: Bearer <user_id>
```
(Requires admin privileges)

Request:
```json
{
  "crypto_type": "USDT",
  "wallet_address": "0x123...abc",
  "network": "Ethereum (ERC-20)",
  "is_active": true
}
```

### Get Site Settings
**GET** `/admin/settings/get_settings/`

No authentication required.

Response:
```json
{
  "company_name": "Broker Invest",
  "support_email": "support@brokerinvest.com",
  "support_phone": "+1-800-000-0000",
  "support_address": "123 Business St, City, Country",
  "footer_text": "© 2024 Broker Invest"
}
```

### Update Site Settings
**POST** `/admin/settings/`

Headers:
```
Authorization: Bearer <user_id>
```
(Requires admin privileges)

Request:
```json
{
  "company_name": "Broker Invest",
  "support_email": "support@brokerinvest.com",
  "support_phone": "+1-800-000-0000",
  "support_address": "123 Business St, New York",
  "footer_text": "© 2024 Broker Invest. All rights reserved."
}
```

### Get Popup Notifications
**GET** `/admin/popup-notifications/recent_notifications/`

No authentication required.

Response:
```json
[
  {
    "id": "uuid",
    "username": "john_doe",
    "amount": 100.00,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": "Amount not within plan range"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 404 Not Found
```json
{
  "error": "Plan not found"
}
```

### 500 Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting
Currently no rate limiting. Implement with Django REST throttling:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## API Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - Auth required |
| 403 | Forbidden - No permission |
| 404 | Not Found - Resource missing |
| 500 | Server Error - Internal error |

---

## Example Client Code

### JavaScript/Fetch
```javascript
// Register
const response = await fetch('http://localhost:8000/api/users/users/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'password123',
    transaction_pin: '1234'
  })
});

// Get investments with auth
const investments = await fetch('http://localhost:8000/api/investments/active/my_investments/', {
  headers: { 'Authorization': 'Bearer <user_id>' }
});
```

### Python/Requests
```python
import requests

# Register
response = requests.post(
  'http://localhost:8000/api/users/users/register/',
  json={
    'username': 'john_doe',
    'password': 'password123',
    'transaction_pin': '1234'
  }
)

# Get investments with auth
headers = {'Authorization': f'Bearer {user_id}'}
investments = requests.get(
  'http://localhost:8000/api/investments/active/my_investments/',
  headers=headers
)
```

---

**Last Updated**: January 2024
**Version**: 1.0.0
