from django.contrib import admin
from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'latitude', 'longitude', 'is_active')
    search_fields = ('name', 'address')
    list_editable = ('is_active',)
