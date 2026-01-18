from django.db import models
from config.utils import compress_image

class Banner(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Banner {self.id}"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = Banner.objects.get(pk=self.pk)
                if old.image != self.image:
                    compress_image(self.image)
            except Banner.DoesNotExist:
                pass
        else:
            compress_image(self.image)
        super().save(*args, **kwargs)

class Feedback(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} ({self.email})"

class AppVersion(models.Model):
    version = models.CharField(max_length=50, help_text="e.g. 1.0.0")
    force_update = models.BooleanField(default=False)
    message = models.TextField(blank=True, help_text="Message to show in the update dialog")
    store_url = models.URLField(blank=True, help_text="Link to Play Store / App Store")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Version {self.version} (Force: {self.force_update})"
    
    class Meta:
        get_latest_by = 'created_at'
