from django.contrib import admin
from .models import Order, OrderItem, DeliveryCharge

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price_at_purchase')
    can_delete = False
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'status', 'payment_method', 'total_amount', 'order_at')
    search_fields = ('user__email', 'id', 'contact_number')

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return (StatusFilter, CreatedAtFilter, PaymentMethodFilter, BranchFilter)
        return (StatusFilter, CreatedAtFilter, PaymentMethodFilter)

    readonly_fields = ('total_amount',)
    inlines = [OrderItemInline]
    list_editable = ('status',)
    list_display_links = ('user',)

    def order_at(self, obj):
        return obj.created_at
    order_at.short_description = 'Order At'
    order_at.admin_order_field = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 1. Superusers see everything
        if request.user.is_superuser:
            return qs
        
        # 2. Managers (is_staff=True, is_superuser=False) see only their branch
        if request.user.branch:
            return qs.filter(branch=request.user.branch)
        
        # 3. If a manager has NO branch assigned, show nothing (Safety fallback)
        return qs.none()

class StatusFilter(admin.SimpleListFilter):
    title = 'Filter by Order Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Order.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class PaymentMethodFilter(admin.SimpleListFilter):
    title = 'Filter by Payment Method'
    parameter_name = 'payment_method'

    def lookups(self, request, model_admin):
        return Order.PAYMENT_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(payment_method=self.value())
        return queryset

class CreatedAtFilter(admin.SimpleListFilter):
    title = 'Filter by Order Time'
    parameter_name = 'created_at_custom'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('past_7_days', 'Past 7 days'),
            ('this_month', 'This month'),
            ('this_year', 'This year'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        import datetime
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        if self.value() == 'past_7_days':
            return queryset.filter(created_at__gte=now - datetime.timedelta(days=7))
        if self.value() == 'this_month':
            return queryset.filter(created_at__month=now.month, created_at__year=now.year)
        if self.value() == 'this_year':
            return queryset.filter(created_at__year=now.year)
        return queryset

class BranchFilter(admin.SimpleListFilter):
    title = 'Filter by Branch Selected'
    parameter_name = 'branch'

    def lookups(self, request, model_admin):
        from branches.models import Branch
        return [(b.id, b.name) for b in Branch.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(branch__id=self.value())
        return queryset

@admin.register(DeliveryCharge)
class DeliveryChargeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'updated_at')
    # Limit to one object in Admin? Not strictly asked but good practice for singleton. 
    # But user said "if there are multiple object in that model return the first one only than", 
    # so standard admin is fine.
