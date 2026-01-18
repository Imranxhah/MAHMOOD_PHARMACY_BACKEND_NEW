from rest_framework import serializers
from .models import Banner, AppVersion

class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ['version', 'force_update', 'message', 'store_url']

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'is_active', 'created_at']
