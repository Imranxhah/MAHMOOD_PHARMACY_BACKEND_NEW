from django.urls import path, include
from .views import (
    RegisterView, 
    VerifyOTPView, 
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    UserProfileView,
    UserListView,
    CustomTokenObtainPairView,
    ResendOTPView,
    ChangePasswordView # Added ChangePasswordView
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/verify/', VerifyOTPView.as_view(), name='verify'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='resend_otp'), # Added resend-otp endpoint
    
    # Password
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password/change/', ChangePasswordView.as_view(), name='password_change'),
    
    # Users
    path('users/profile/', UserProfileView.as_view(), name='user_profile'),
    path('users/', UserListView.as_view(), name='user_list'),
]

from rest_framework.routers import DefaultRouter
from .views import AddressViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns += router.urls

