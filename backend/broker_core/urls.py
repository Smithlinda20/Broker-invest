from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Frontend pages
    path('', include('broker_platform.urls')),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/investments/', include('investments.urls')),
    path('api/admin/', include('admin_panel.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # Django admin (keep for superuser management)
    path('backend/admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
