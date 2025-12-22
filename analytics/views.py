from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status, renderers
from rest_framework.authentication import SessionAuthentication
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth, TruncDay
from django.utils.timezone import now
from datetime import timedelta
from orders.models import Order
from users.models import User
from products.models import Product
import json
from django.core.serializers.json import DjangoJSONEncoder

class DashboardStatsView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_sales = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = Order.objects.count()
        total_users = User.objects.count()
        low_stock_products = Product.objects.filter(stock__lt=10).count()

        # Recent 5 Orders
        recent_orders = Order.objects.order_by('-created_at')[:5].values(
            'id', 'user__email', 'total_amount', 'status', 'created_at'
        )

        return Response({
            "total_sales": total_sales,
            "total_orders": total_orders,
            "total_users": total_users,
            "low_stock_count": low_stock_products,
            "recent_orders": recent_orders
        })



class AnalyticsHubView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'admin/analytics_dashboard.html'

    def get(self, request):
        return Response({})

class AnalyticsReportView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'admin/analytics_report.html'

    def get(self, request, report_type):
        from branches.models import Branch
        branch_id = request.GET.get('branch', 'all')
        branches = Branch.objects.all().values('id', 'name')
        
        # Base Querysets
        orders = Order.objects.all()
        if branch_id != 'all':
            orders = orders.filter(branch_id=branch_id)
            
        data = {}
        chart_type = 'bar' # Default
        title = "Report"

        if report_type == 'sales_trend': # Keep for legacy redirect if needed, or remove. Let's redirect logic.
            # Fallback to monthly if someone hits old URL, or just perform monthly
            report_type = 'monthly_sales'
        
        if report_type == 'daily_sales':
            title = "Daily Sales (Last 30 Days)"
            thirty_days_ago = now() - timedelta(days=30)
            daily = orders.filter(created_at__gte=thirty_days_ago).annotate(
                day=TruncDay('created_at')
            ).values('day').annotate(total=Sum('total_amount')).order_by('day')
            
            data = [{'day': x['day'].strftime('%Y-%m-%d'), 'total': float(x['total'])} for x in daily]
            chart_type = 'line'

        elif report_type == 'monthly_sales':
            title = "Monthly Sales (Last 6 Months)"
            six_months_ago = now() - timedelta(days=180)
            monthly = orders.filter(created_at__gte=six_months_ago).annotate(
                period=TruncMonth('created_at')
            ).values('period').annotate(total=Sum('total_amount')).order_by('period')
            
            data = [{'period': x['period'].strftime('%Y-%m'), 'total': float(x['total'])} for x in monthly]
            chart_type = 'line'

        elif report_type == 'top_customers':
            title = "Top 10 Customers"
            # Annotate manually because we need to filter orders inside the annotation
            # Standard annotation User.objects.annotate(sum=Sum('orders__total')) doesn't respect external filter easily without Subquery
            # Simplest for this scale: ID list approach or filtering
            
            # Better approach: Filter Order first, then aggregate by User
            top_users = orders.values('user__email').annotate(
                total_spent=Sum('total_amount')
            ).order_by('-total_spent')[:10]
            
            data = [{'email': x['user__email'], 'total_spent': x['total_spent']} for x in top_users]

        elif report_type == 'top_products':
            title = "Top 10 Selling Products"
            # Filter OrderItems by the filtered orders
            top_prods = Order.objects.filter(id__in=orders.values('id')).values('items__product__name').annotate(
                count=Sum('items__quantity')
            ).order_by('-count')[:10]
            
            # Cleaning up the key name
            data = [{'name': x['items__product__name'], 'count': x['count']} for x in top_prods]

        elif report_type == 'top_categories': # NEW
            title = "Top Selling Categories"
            top_cats = Order.objects.filter(id__in=orders.values('id')).values('items__product__category__name').annotate(
                count=Sum('items__quantity')
            ).order_by('-count')[:10]
            
            data = [{'name': x['items__product__category__name'], 'count': x['count']} for x in top_cats]
            chart_type = 'pie'

        elif report_type == 'order_status':
            title = "Order Status Ratio"
            status_counts = orders.values('status').annotate(count=Count('id'))
            data = list(status_counts)
            chart_type = 'doughnut'

        elif report_type == 'branch_sales':
            title = "Orders per Branch"
            # For this report, 'all' branch filter doesn't make sense if we want to compare branches
            # But if user selects a branch, we show only that branch's bar? Yes.
            branch_counts = orders.exclude(branch__isnull=True).values('branch__name').annotate(count=Count('id')).order_by('-count')
            data = list(branch_counts)

        context = {
            'report_type': report_type,
            'title': title,
            'chart_type': chart_type,
            'data': json.dumps(data, cls=DjangoJSONEncoder),
            'branches': list(branches),
            'selected_branch': int(branch_id) if branch_id != 'all' else 'all'
        }
        return Response(context)

