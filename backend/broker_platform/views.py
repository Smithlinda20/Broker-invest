from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


@method_decorator(ensure_csrf_cookie, name='dispatch')
class HomePageView(TemplateView):
    """Serve the main homepage"""
    template_name = 'index.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    """Serve the dashboard (requires login)"""
    template_name = 'dashboard/dashboard.html'
    login_url = '/login/'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginPageView(TemplateView):
    """Serve the login page"""
    template_name = 'auth/login.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class RegisterPageView(TemplateView):
    """Serve the registration page"""
    template_name = 'auth/register.html'
