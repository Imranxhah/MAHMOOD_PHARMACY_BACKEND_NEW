from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Banner
from .serializers import BannerSerializer

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = BannerSerializer
    permission_classes = [AllowAny] # Everyone receives banners

    def get_permissions(self):
         if self.action in ['create', 'update', 'partial_update', 'destroy']:
             return [IsAdminUser()]
         return [AllowAny()]

class SendNotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        title = request.data.get('title')
        body = request.data.get('body')
        
        if not title or not body:
             return Response({"error": "Title and Body required."}, status=status.HTTP_400_BAD_REQUEST)
             
        # Placeholder for Firebase Logic
        # 1. Get all FCM tokens from users (requires adding fcm_token field to User model)
        # 2. Use firebase_admin to send multicast message
        
        return Response({"success": True, "message": f"Notification '{title}' queued for sending."}, status=status.HTTP_200_OK)
