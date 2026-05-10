from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(TemplateView):
    """Serve the main homepage"""
    template_name = 'index.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Serve the dashboard (requires login)"""
    template_name = 'dashboard/dashboard.html'
    login_url = '/login/'


class LoginPageView(TemplateView):
    """Serve the login page"""
    template_name = 'auth/login.html'


class RegisterPageView(TemplateView):
    """Serve the registration page"""
    template_name = 'auth/register.html'
