from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from .models import User

# Unregister original User admin if needed, but we implemented a custom model so we likely haven't registered it purely yet or used a basic one.
# Let's check users/admin.py first? No, I'll just write a robust one.
# Re-reading: The user has a custom user model. Standard admin might not be showing stats.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile', 'is_staff', 'branch', 'order_count', 'total_spent_display')
    search_fields = ('email', 'mobile', 'first_name')
    list_filter = ('is_staff', 'is_active', 'branch')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _order_count=Count('orders'),
            _total_spent=Sum('orders__total_amount')
        )
        return queryset

    def order_count(self, obj):
        return obj._order_count
    order_count.admin_order_field = '_order_count'
    order_count.short_description = 'Orders Placed'

    def total_spent_display(self, obj):
        return f"${obj._total_spent}" if obj._total_spent else "$0.00"
    total_spent_display.admin_order_field = '_total_spent'
    total_spent_display.short_description = 'Total Spent'
