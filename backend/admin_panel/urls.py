from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminNotificationViewSet, PaymentWalletViewSet, SiteSettingsViewSet, PopupNotificationViewSet

router = DefaultRouter()
router.register(r'notifications', AdminNotificationViewSet)
router.register(r'payment-wallets', PaymentWalletViewSet)
router.register(r'settings', SiteSettingsViewSet)
router.register(r'popup-notifications', PopupNotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
