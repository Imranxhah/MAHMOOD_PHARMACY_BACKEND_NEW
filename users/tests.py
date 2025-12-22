from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from django.core.cache import cache

User = get_user_model()

from django.test import override_settings

# Override throttling for tests to prevent 429 errors
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '1000/day',
        'otp': '1000/min', 
    }
})
class AuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.register_url = reverse('register')
        self.verify_url = reverse('verify')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'mobile': '+1234567890'
        }

    def test_registration_creates_inactive_user_and_sends_email(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.otp_code)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.otp_code, mail.outbox[0].body)

    def test_verify_otp_activates_user(self):
        # Register
        self.client.post(self.register_url, self.user_data)
        user = User.objects.get(email='test@example.com')
        
        # Verify
        data = {'email': user.email, 'otp_code': user.otp_code}
        response = self.client.post(self.verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertIsNone(user.otp_code)

    def test_verify_otp_fails_with_wrong_code_and_counts_attempts(self):
        self.client.post(self.register_url, self.user_data)
        user = User.objects.get(email='test@example.com')
        
        data = {'email': user.email, 'otp_code': '000000'} # Wrong code
        response = self.client.post(self.verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertEqual(user.otp_attempts, 1)

    def test_verify_otp_fails_if_expired(self):
        self.client.post(self.register_url, self.user_data)
        user = User.objects.get(email='test@example.com')
        
        # Expire OTP manually
        user.otp_created_at = timezone.now() - timedelta(minutes=11)
        user.save()
        
        data = {'email': user.email, 'otp_code': user.otp_code}
        response = self.client.post(self.verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired", str(response.data))

    def test_registration_atomic_rollback(self):
        # Mock send_mail to raise exception
        with patch('users.views.send_otp_email', side_effect=Exception("SMTP Fail")):
            response = self.client.post(self.register_url, self.user_data)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(User.objects.count(), 0) # Should be 0 due to atomic rollback

    def test_duplicate_email_registration(self):
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure message is clean
        self.assertTrue('email' in response.data)

    def test_password_security(self):
        self.user_data['password'] = '123'
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
