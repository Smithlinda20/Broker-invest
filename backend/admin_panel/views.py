from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import AdminNotification, PaymentWallet, SiteSettings, PopupNotification
from .serializers import AdminNotificationSerializer, PaymentWalletSerializer, SiteSettingsSerializer, PopupNotificationSerializer

class AdminNotificationViewSet(viewsets.ModelViewSet):
    queryset = AdminNotification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = AdminNotification.objects.filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

class PaymentWalletViewSet(viewsets.ModelViewSet):
    queryset = PaymentWallet.objects.all()
    serializer_class = PaymentWalletSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def get_settings(self, request):
        try:
            settings = SiteSettings.objects.first()
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        except SiteSettings.DoesNotExist:
            return Response({'error': 'Settings not found'}, status=status.HTTP_404_NOT_FOUND)

class PopupNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PopupNotification.objects.all()
    serializer_class = PopupNotificationSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def recent_notifications(self, request):
        notifications = PopupNotification.objects.all()[:10]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
