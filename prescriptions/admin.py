from django.contrib import admin
from django.utils.html import format_html
from .models import Prescription
from branches.models import Branch

class StatusFilter(admin.SimpleListFilter):
    title = 'Filter by Prescription Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return Prescription.STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class BranchFilter(admin.SimpleListFilter):
    title = 'Filter by Branch'
    parameter_name = 'branch'

    def lookups(self, request, model_admin):
        return [(b.id, b.name) for b in Branch.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(branch__id=self.value())
        return queryset

class CreatedAtFilter(admin.SimpleListFilter):
    title = 'Filter by Upload Time'
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

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'branch', 'status', 'created_at', 'image_preview')
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return (StatusFilter, BranchFilter, CreatedAtFilter)
        return (StatusFilter, CreatedAtFilter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.branch:
            return qs.filter(branch=request.user.branch)
        return qs
    search_fields = ('user__email', 'id')
    readonly_fields = ('created_at',)
    list_editable = ('status',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="width: 50px; height: 50px; object-fit: cover;" /></a>', obj.image.url, obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.branch:
            obj.branch = request.user.branch
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and request.user.branch:
            return self.readonly_fields + ('branch',)
        return self.readonly_fields
