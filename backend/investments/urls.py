from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (InvestmentPlanViewSet, ActiveInvestmentViewSet, WithdrawHistoryViewSet,
                    CopyTradingViewSet, CryptoSwapViewSet)

router = DefaultRouter()
router.register(r'plans', InvestmentPlanViewSet)
router.register(r'active', ActiveInvestmentViewSet)
router.register(r'history', WithdrawHistoryViewSet)
router.register(r'copy-trading', CopyTradingViewSet, basename='copy-trading')
router.register(r'crypto-swap', CryptoSwapViewSet, basename='crypto-swap')

urlpatterns = [
    path('', include(router.urls)),
]

# New routes:
# GET  /api/investments/copy-trading/top-traders/
# GET  /api/investments/copy-trading/my-allocations/
# POST /api/investments/copy-trading/follow/
# POST /api/investments/crypto-swap/create/
# GET  /api/investments/crypto-swap/my-swaps/
