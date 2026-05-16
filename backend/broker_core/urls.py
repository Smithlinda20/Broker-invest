from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from admin_panel.views import (
    admin_api_activities,
    admin_api_confirm_payment,
    admin_api_reject_payment,
    admin_api_summary,
    admin_api_users,
    admin_dashboard_view,
    admin_login_view,
    admin_logout_view,
)

urlpatterns = [
    # Frontend pages
    path('', include('broker_platform.urls')),
    
    # Admin custom auth
    path('backend/login/', admin_login_view, name='admin_login'),
    path('backend/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('backend/logout/', admin_logout_view, name='admin_logout'),
    path('backend/api/summary/', admin_api_summary, name='admin_api_summary'),
    path('backend/api/users/', admin_api_users, name='admin_api_users'),
    path('backend/api/activities/', admin_api_activities, name='admin_api_activities'),
    path('backend/api/confirm-payment/', admin_api_confirm_payment, name='admin_api_confirm_payment'),
    path('backend/api/reject-payment/', admin_api_reject_payment, name='admin_api_reject_payment'),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/investments/', include('investments.urls')),
    path('api/admin/', include('admin_panel.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # Django admin (keep for superuser management)
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
