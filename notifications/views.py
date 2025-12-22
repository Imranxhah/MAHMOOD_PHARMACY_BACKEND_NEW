from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Notification, BroadcastNotification
from .serializers import NotificationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    # permission_classes = [IsAuthenticated] # Moved to get_permissions
    http_method_names = ['get', 'patch', 'delete', 'post']

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Notification.objects.filter(user=self.request.user).order_by('-created_at')
        return Notification.objects.none()

    def list(self, request, *args, **kwargs):
        # 1. Fetch Broadcast Notifications (for everyone)
        broadcasts = BroadcastNotification.objects.all().order_by('-created_at')
        
        # Helper: Map broadcast ID to status for auth users
        broadcast_status_map = {}
        if request.user.is_authenticated:
            from .models import BroadcastStatus
            statuses = BroadcastStatus.objects.filter(user=request.user)
            broadcast_status_map = {s.broadcast_id: s for s in statuses}

        broadcast_data = []
        for b in broadcasts:
            # Check status for auth user
            is_read = False
            is_deleted = False
            
            if request.user.is_authenticated and b.id in broadcast_status_map:
                status_obj = broadcast_status_map[b.id]
                is_read = status_obj.is_read
                is_deleted = status_obj.is_deleted

            if not is_deleted:
                broadcast_data.append({
                    "id": -b.id, # Negative ID for broadcasts
                    "title": b.title,
                    "body": b.body,
                    "is_read": is_read,
                    "created_at": b.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

        # 2. Fetch User Notifications (if auth)
        user_data = []
        if request.user.is_authenticated:
            user_notifs = self.get_queryset()
            serializer = self.get_serializer(user_notifs, many=True)
            user_data = serializer.data
        
        # 3. Combine and Sort
        combined_data = broadcast_data + user_data
        combined_data.sort(key=lambda x: x['created_at'], reverse=True)

        return Response(combined_data)

    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion. If ID < 0, it's a broadcast.
        """
        try:
            pk = int(kwargs.get('pk'))
        except (ValueError, TypeError):
             return super().destroy(request, *args, **kwargs)

        if pk < 0:
            # Handle Broadcast Deletion
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            broadcast_id = abs(pk)
            try:
                broadcast = BroadcastNotification.objects.get(id=broadcast_id)
                from .models import BroadcastStatus
                status_obj, _ = BroadcastStatus.objects.get_or_create(user=request.user, broadcast=broadcast)
                status_obj.is_deleted = True
                status_obj.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except BroadcastNotification.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            # Normal Notification Deletion
            return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle updates (e.g. marking as read). If ID < 0, it's a broadcast.
        """
        try:
            pk = int(kwargs.get('pk'))
        except (ValueError, TypeError):
             return super().partial_update(request, *args, **kwargs)

        if pk < 0:
            # Handle Broadcast Update
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            broadcast_id = abs(pk)
            try:
                broadcast = BroadcastNotification.objects.get(id=broadcast_id)
                from .models import BroadcastStatus
                status_obj, _ = BroadcastStatus.objects.get_or_create(user=request.user, broadcast=broadcast)
                
                # Update fields if present in request data
                if 'is_read' in request.data:
                    status_obj.is_read = request.data['is_read']
                
                status_obj.save()
                return Response({"message": "Broadcast updated"}, status=status.HTTP_200_OK)
            except BroadcastNotification.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
             return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='register-device')
    def register_device(self, request):
        """
        Endpoint to register FCM Token.
        Payload: { "fcm_token": "..." }
        """
        fcm_token = request.data.get('fcm_token')
        if not fcm_token:
            return Response({"error": "fcm_token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.fcm_token = fcm_token
        user.save()
        
        return Response({"message": "Device registered successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """
        Mark all notifications as read.
        """
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "All notifications marked as read"}, status=status.HTTP_200_OK)
