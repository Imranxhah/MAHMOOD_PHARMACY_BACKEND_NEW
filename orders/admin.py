from django.contrib import admin
from .models import Order, OrderItem, DeliveryCharge

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    autocomplete_fields = ['product']
    extra = 1
    readonly_fields = ['product_image_preview']

    def product_image_preview(self, obj):
        if obj.product and obj.product.image:
            from django.utils.html import mark_safe
            return mark_safe(f'<img src="{obj.product.image.url}" class="admin-product-image" />')
        return "No Image"
    product_image_preview.short_description = "Product Image"

    fields = ('product', 'product_image_preview', 'unit_type', 'quantity', 'price_at_purchase', 'is_manual_price')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        from django import forms
        formset.form.base_fields['is_manual_price'].widget = forms.HiddenInput()
        formset.form.base_fields['price_at_purchase'].widget = forms.HiddenInput()
        return formset

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'status', 'order_type', 'total_amount', 'order_at')
    search_fields = ('user__email', 'id', 'contact_number')

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return (StatusFilter, CreatedAtFilter, OrderTypeFilter, BranchFilter)
        return (StatusFilter, CreatedAtFilter, OrderTypeFilter)

    readonly_fields = ('total_amount',)
    inlines = [OrderItemInline]
    list_editable = ('status',)
    list_display_links = ('user',)

    class Media:
        js = ('js/admin_order.js',)

    def order_at(self, obj):
        return obj.created_at
    order_at.short_description = 'Order At'
    order_at.admin_order_field = 'created_at'

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        prescription_id = request.GET.get('prescription_id')
        if prescription_id:
            try:
                from prescriptions.models import Prescription
                prescription = Prescription.objects.get(id=prescription_id)
                initial['user'] = prescription.user
                initial['branch'] = prescription.branch
                initial['shipping_address'] = prescription.address
                initial['contact_number'] = prescription.contact_number
                # Using 'notes' as generic name or description if helpful? No, user asked for specific fields.
            except Prescription.DoesNotExist:
                pass
        return initial

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

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # For new orders, trigger a second save after items are added
        # to ensure the "Order Placed" notification signal with items is fired.
        if not change:
            form.instance.refresh_from_db()  # Ensure we have the updated total_amount from signals
            form.instance.save()

class StatusFilter(admin.SimpleListFilter):
    title = 'Filter by Order Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Order.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class OrderTypeFilter(admin.SimpleListFilter):
    title = 'Filter by Order Type'
    parameter_name = 'order_type'

    def lookups(self, request, model_admin):
        return Order.ORDER_TYPE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(order_type=self.value())
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
