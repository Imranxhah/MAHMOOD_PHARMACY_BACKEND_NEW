from rest_framework import serializers
from .models import Prescription

class PrescriptionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    status = serializers.CharField(read_only=True)
    admin_feedback = serializers.CharField(read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'user', 'branch', 'image', 'notes', 'contact_number', 'status', 'admin_feedback', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
