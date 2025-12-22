from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    latitude = models.FloatField(help_text="Decimal Coordinate (e.g. 33.6844)")
    longitude = models.FloatField(help_text="Decimal Coordinate (e.g. 73.0479)")
    timing = models.CharField(max_length=100, default="9:00 AM - 11:00 PM")
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='branches/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name
