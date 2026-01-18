from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'is_read', 'created_at', 'data']

    def get_data(self, obj):
        if obj.order:
            return {
                "type": "order",
                "order_id": obj.order.id
            }
        return {}
