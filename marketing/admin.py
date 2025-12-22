from django.contrib import admin
from django.utils.html import format_html
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'image_preview')
    list_editable = ('is_active',)
    search_fields = ('title',)

    def image_preview(self, obj):
        if obj.image:
             return format_html('<img src="{}" style="width: 100px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Banner Image'
