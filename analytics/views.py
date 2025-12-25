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
import matplotlib
matplotlib.use('Agg') # Set backend to non-interactive
import matplotlib.pyplot as plt
import io
import base64
from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import os
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from .forms import SalesReportForm
from orders.models import OrderItem

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




@staff_member_required
def sales_report_view(request):
    if request.method == 'POST':
        form = SalesReportForm(request.POST)
        if form.is_valid():
            # Get cleaned data
            branch = form.cleaned_data.get('branch')
            category = form.cleaned_data.get('category')
            product = form.cleaned_data.get('product')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # Build Query
            items = OrderItem.objects.filter(
                order__created_at__date__gte=start_date,
                order__created_at__date__lte=end_date
            ).exclude(
                product__isnull=True
            ).select_related('order', 'product', 'order__branch', 'product__category').annotate(
                total_price=F('quantity') * F('price_at_purchase')
            )

            if branch:
                items = items.filter(order__branch=branch)
            if category:
                items = items.filter(product__category=category)
            if product:
                items = items.filter(product=product)

            # Calculate Grand Total
            total_revenue = items.aggregate(
                total=Sum(F('quantity') * F('price_at_purchase'))
            )['total'] or 0

            # Generate PDF via WeasyPrint
            template_path = 'analytics/pdf_template.html'
            context = {
                'items': items,
                'start_date': start_date,
                'end_date': end_date,
                'branch': branch if branch else "All Branches",
                'category': category if category else "All Categories",
                'product': product if product else "All Products",
                'total_revenue': total_revenue,
            }
            
            html_string = render_to_string(template_path, context)

            response = HttpResponse(content_type='application/pdf')
            timestamp = now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_report_{timestamp}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Anti-caching headers for IDM/Browsers
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
            
            return response
    else:
        form = SalesReportForm()

    return render(request, 'analytics/sales_report.html', {'form': form, 'title': 'Generate Sales Report'})

@staff_member_required
def visual_report_view(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # --- Common Filters ---
        orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        order_items = OrderItem.objects.filter(order__in=orders)

        # Helper to generate base64 plot
        def get_plot_url():
            img = io.BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            return f"data:image/png;base64,{plot_url}"

        # ==========================================
        # SECTION 1: BRANCH ANALYSIS
        # ==========================================
        # 1a. Branch by Orders
        branch_data_orders = orders.exclude(branch__isnull=True).values('branch__name').annotate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-total_orders')

        # 1b. Branch by Revenue
        branch_data_revenue = orders.exclude(branch__isnull=True).values('branch__name').annotate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-total_revenue')
        
        # 1a. Branch Orders Chart
        plt.figure(figsize=(10, 6))
        # Use reversed lists so the highest value is at the top
        plt.barh([x['branch__name'] for x in branch_data_orders][::-1], [x['total_orders'] for x in branch_data_orders][::-1], color='#1abc9c')
        plt.title('Orders per Branch')
        plt.xlabel('Number of Orders')
        plt.tight_layout()
        branch_orders_chart = get_plot_url()

        # 1b. Branch Revenue Chart
        plt.figure(figsize=(10, 6))
        plt.barh([x['branch__name'] for x in branch_data_revenue][::-1], [x['total_revenue'] for x in branch_data_revenue][::-1], color='#3498db')
        plt.title('Revenue per Branch')
        plt.xlabel('Revenue (PKR)')
        plt.tight_layout()
        branch_revenue_chart = get_plot_url()

        # ==========================================
        # SECTION 2: CATEGORY ANALYSIS
        # ==========================================
        # 2a. Category by Orders
        category_data_orders = order_items.values('product__category__name').annotate(
            total_orders=Count('id'), 
            total_revenue=Sum(F('quantity') * F('price_at_purchase'))
        ).order_by('-total_orders')

        # 2b. Category by Revenue
        category_data_revenue = order_items.values('product__category__name').annotate(
            total_orders=Count('id'), 
            total_revenue=Sum(F('quantity') * F('price_at_purchase'))
        ).order_by('-total_revenue')

        # 2a. Category Orders Chart
        plt.figure(figsize=(8, 6))
        plt.pie([x['total_orders'] for x in category_data_orders], labels=[x['product__category__name'] for x in category_data_orders], autopct='%1.1f%%', startangle=140, colors=plt.cm.Set3.colors)
        plt.title('Sales Volume per Category')
        plt.tight_layout()
        category_orders_chart = get_plot_url()

        # 2b. Category Revenue Chart
        plt.figure(figsize=(8, 6))
        plt.pie([x['total_revenue'] for x in category_data_revenue], labels=[x['product__category__name'] for x in category_data_revenue], autopct='%1.1f%%', startangle=140, colors=plt.cm.Set3.colors)
        plt.title('Revenue per Category')
        plt.tight_layout()
        category_revenue_chart = get_plot_url()

        # ==========================================
        # SECTION 3: TOP PRODUCTS
        # ==========================================
        # 3a. Top Products by Quantity
        top_products_qty = order_items.values('product__name').annotate(
            qty_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price_at_purchase'))
        ).order_by('-qty_sold')[:10]

        # 3b. Top Products by Revenue
        top_products_revenue = order_items.values('product__name').annotate(
            qty_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price_at_purchase'))
        ).order_by('-revenue')[:10]

        # Chart 3a: Qty
        plt.figure(figsize=(10, 6))
        plt.barh([x['product__name'] for x in top_products_qty][::-1], [x['qty_sold'] for x in top_products_qty][::-1], color='#f39c12')
        plt.title('Top 10 Products (Quantity Sold)')
        plt.xlabel('Quantity')
        plt.tight_layout()
        product_qty_chart = get_plot_url()

        # Chart 3b: Revenue
        plt.figure(figsize=(10, 6))
        plt.barh([x['product__name'] for x in top_products_revenue][::-1], [x['revenue'] for x in top_products_revenue][::-1], color='#2ecc71')
        plt.title('Top 10 Products (Revenue Generated)')
        plt.xlabel('Revenue')
        plt.tight_layout()
        product_revenue_chart = get_plot_url()

        # ==========================================
        # SECTION 4: TRENDS
        # ==========================================
        # 4a. Overall Sales Trend
        daily_sales = orders.annotate(day=TruncDay('created_at')).values('day').annotate(
            daily_revenue=Sum('total_amount')
        ).order_by('day')
        
        dates = [x['day'].strftime('%Y-%m-%d') for x in daily_sales]
        revenues = [x['daily_revenue'] for x in daily_sales]

        plt.figure(figsize=(12, 6))
        plt.plot(dates, revenues, marker='o', linestyle='-', color='#8e44ad', linewidth=2)
        plt.fill_between(dates, revenues, color='#8e44ad', alpha=0.3)
        plt.title('Daily Sales Trend')
        plt.xlabel('Date')
        plt.ylabel('Revenue')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        overall_trend_chart = get_plot_url()

        context = {
            'start_date': start_date,
            'end_date': end_date,
            'branch_data_orders': branch_data_orders,
            'branch_data_revenue': branch_data_revenue,
            'branch_orders_chart': branch_orders_chart,
            'branch_revenue_chart': branch_revenue_chart,
            'category_data_orders': category_data_orders,
            'category_data_revenue': category_data_revenue,
            'category_orders_chart': category_orders_chart,
            'category_revenue_chart': category_revenue_chart,
            'top_products_qty': top_products_qty,
            'top_products_revenue': top_products_revenue,
            'product_qty_chart': product_qty_chart,
            'product_revenue_chart': product_revenue_chart,
            'overall_trend_chart': overall_trend_chart,
        }

        # Generate PDF
        html_string = render_to_string('analytics/visual_report.html', context)
        response = HttpResponse(content_type='application/pdf')
        filename = f"Visual_Report_{now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Anti-caching headers for IDM/Browsers
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
        return response

    return HttpResponse("Method not allowed", status=405)
