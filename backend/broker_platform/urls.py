from django.urls import path
from .views import HomePageView, DashboardView, LoginPageView, RegisterPageView

app_name = 'broker_platform'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', RegisterPageView.as_view(), name='register'),
]
