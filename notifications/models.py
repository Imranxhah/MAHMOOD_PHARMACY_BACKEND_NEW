from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    def __str__(self):
        return f"Notification for {self.user.email} - {self.title}"

    class Meta:
        ordering = ['-created_at']

class BroadcastNotification(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Broadcast: {self.title}"

    class Meta:
        verbose_name = "Broadcast Notification"
        verbose_name_plural = "Broadcast Notifications"

class BroadcastStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    broadcast = models.ForeignKey(BroadcastNotification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'broadcast')
        verbose_name = "Broadcast Status"
        verbose_name_plural = "Broadcast Statuses"
