from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, WithdrawalViewSet, ReferralViewSet, UserProfileViewSet, ImportedWalletViewSet

router = DefaultRouter()
router.register(r'users', UserRegistrationView, basename='users')
router.register(r'withdrawals', WithdrawalViewSet, basename='withdrawals')
router.register(r'referrals', ReferralViewSet, basename='referrals')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'wallets', ImportedWalletViewSet, basename='wallets')

urlpatterns = [
    path('', include(router.urls)),
]

# This auto-generates these routes:
# POST /api/users/users/register/   ← register
# POST /api/users/users/login/      ← login  (creates Django session)
# POST /api/users/users/logout/     ← logout (destroys Django session)
# POST /api/users/profile/change_password/  ← change password
# POST /api/users/profile/update_pin/      ← update PIN
# POST /api/users/wallets/import_wallet/   ← import wallet
# GET  /api/users/wallets/my_wallets/      ← get imported wallets