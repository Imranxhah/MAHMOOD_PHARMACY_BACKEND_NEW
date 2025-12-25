from rest_framework.throttling import ScopedRateThrottle
from django.core.exceptions import ImproperlyConfigured

class RobustOTPThrottle(ScopedRateThrottle):
    """
    A robust ScopedRateThrottle that defaults to '5/min' if the 'otp' scope 
    is missing from settings, preventing Internal Server Errors.
    """
    scope = 'otp'
    
    def get_rate(self):
        try:
            return super().get_rate()
        except (ImproperlyConfigured, KeyError):
            # Fallback to a safe default if configuration is missing
            return '5/min'
