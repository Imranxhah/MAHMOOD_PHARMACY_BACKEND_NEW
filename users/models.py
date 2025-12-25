from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    
    mobile_validator = RegexValidator(
        regex=r'^03\d{9}$',
        message="Phone number must be 11 digits and start with 03 (e.g., 03XXXXXXXXX) with no spaces or characters."
    )
    mobile = models.CharField(validators=[mobile_validator], max_length=11, blank=True)
    
    # Manager Branch Link
    branch = models.ForeignKey(
        'branches.Branch', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managers',
        help_text="The branch this user manages (if they are a manager)."
    )
    
    # OTP Fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.IntegerField(default=0)
    
    # FCM Token
    fcm_token = models.CharField(max_length=2048, blank=True, null=True, help_text="Firebase Cloud Messaging Token for Push Notifications")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.address[:30]}"
