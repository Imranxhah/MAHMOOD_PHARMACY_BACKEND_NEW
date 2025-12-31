from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Sum
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The logic for hashing passwords is in BaseUserAdmin
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    # 1. List View Settings
    ordering = ['email']
    list_display = ('email', 'first_name', 'last_name', 'mobile', 'is_staff', 'branch', 'order_count', 'total_spent_display')
    search_fields = ('email', 'mobile', 'first_name')
    list_filter = ('is_staff', 'is_active', 'branch')
    
    # 2. Edit User Page (Change Form)
    # We must override this because the default uses 'username' which we don't have.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'mobile')}),
        ('Branch Allocation', {'fields': ('branch',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # 3. Add User Page (Creation Form)
    # This controls what fields are shown when creating a NEW user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'mobile', 'branch', 'password1', 'password2'),
        }),
    )

    # 4. Custom Methods from previous implementation
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
        return f"PKR {obj._total_spent}" if obj._total_spent else "PKR 0.00"
    total_spent_display.admin_order_field = '_total_spent'
    total_spent_display.short_description = 'Total Spent'
