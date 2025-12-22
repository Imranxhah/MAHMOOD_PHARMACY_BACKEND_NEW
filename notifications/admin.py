from django.contrib import admin
from .models import Notification, BroadcastNotification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'is_read')
    search_fields = ('user__email', 'title', 'body')
    list_filter = ('is_read', 'created_at')

@admin.register(BroadcastNotification)
class BroadcastNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'body')

