from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from config.utils import compress_image

class Prescription(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    branch = models.ForeignKey(
        'branches.Branch', 
        related_name='prescriptions', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prescriptions', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='prescriptions/')
    phone_regex = RegexValidator(
        regex=r'^03\d{9}$',
        message="Phone number must be 11 digits and start with 03 (e.g., 03XXXXXXXXX) with no spaces or characters."
    )
    contact_number = models.CharField(
        max_length=11, 
        validators=[phone_regex], 
        blank=True, 
        null=True, 
        help_text="Contact number (e.g. 03128424013)"
    )
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_feedback = models.TextField(blank=True, help_text="Reason for rejection or approval notes.")
    note = models.TextField(blank=True, null=True, help_text="Note for the pharmacist.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription by {self.user.email} - {self.status}"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = Prescription.objects.get(pk=self.pk)
                if old.image != self.image:
                    compress_image(self.image)
            except Prescription.DoesNotExist:
                pass
        else:
            compress_image(self.image)
        super().save(*args, **kwargs)
