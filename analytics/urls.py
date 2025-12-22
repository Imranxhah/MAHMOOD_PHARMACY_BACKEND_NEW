from django.urls import path
from .views import DashboardStatsView, AnalyticsHubView, AnalyticsReportView

urlpatterns = [
    path('analytics/dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('charts/', AnalyticsHubView.as_view(), name='admin-charts'),
    path('reports/<str:report_type>/', AnalyticsReportView.as_view(), name='analytics-report'),
]
