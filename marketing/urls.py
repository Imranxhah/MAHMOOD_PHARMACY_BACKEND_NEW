from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BannerViewSet, SendNotificationView, AppVersionView

router = DefaultRouter()
router.register(r'marketing/banners', BannerViewSet, basename='banner')

urlpatterns = [
    path('marketing/app-version/', AppVersionView.as_view(), name='app-version'),
    path('marketing/notifications/send/', SendNotificationView.as_view(), name='send-notification'),
    path('', include(router.urls)),
]
