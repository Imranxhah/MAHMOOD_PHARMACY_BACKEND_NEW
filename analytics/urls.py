from django.urls import path
from .views import DashboardStatsView, AnalyticsHubView, AnalyticsReportView, sales_report_view, visual_report_view

urlpatterns = [
    path('analytics/dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('charts/', AnalyticsHubView.as_view(), name='admin-charts'),
    path('reports/sales/', sales_report_view, name='sales_report'),
    path('reports/visual/', visual_report_view, name='visual_report'),
    path('reports/<str:report_type>/', AnalyticsReportView.as_view(), name='analytics-report'),
]
