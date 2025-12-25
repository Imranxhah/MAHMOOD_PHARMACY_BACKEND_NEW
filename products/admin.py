from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import Category, Product, Favorite
from .resources import CategoryResource, ProductResource

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('name', 'product_count', 'created_at')
    search_fields = ('name',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

from django.db.models import Sum

from django.db.models import Sum

class CategoryFilter(admin.SimpleListFilter):
    title = 'Filter by Product Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Category.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__id=self.value())
        return queryset

class IsActiveFilter(admin.SimpleListFilter):
    title = 'Filter by Active Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Active'),
            ('0', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        if self.value() == '0':
            return queryset.filter(is_active=False)
        return queryset

class CreatedAtFilter(admin.SimpleListFilter):
    title = 'Filter by Creation Time'
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

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'category', 'price', 'stock', 'times_sold', 'is_active', 'image_preview')
    list_filter = (CategoryFilter, IsActiveFilter, CreatedAtFilter)


    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_active')
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(times_sold_count=Sum('order_items__quantity'))

    def times_sold(self, obj):
        return obj.times_sold_count or 0
    times_sold.admin_order_field = 'times_sold_count'
    times_sold.short_description = 'Units Sold'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__name')
