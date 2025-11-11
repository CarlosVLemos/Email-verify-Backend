"""
URLs para Analytics API
Endpoints para dashboard e visualizações
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/overview/', views.DashboardOverviewView.as_view(), name='dashboard_overview'),
    path('dashboard/trends/', views.ProductivityTrendView.as_view(), name='productivity_trends'),
    path('dashboard/categories/', views.CategoryDistributionView.as_view(), name='category_distribution'),
    path('dashboard/senders/', views.SenderAnalysisView.as_view(), name='sender_analysis'),
    path('dashboard/keywords/', views.KeywordInsightsView.as_view(), name='keyword_insights'),
    path('dashboard/performance/', views.PerformanceMetricsView.as_view(), name='performance_metrics'),
    path('emails/', views.EmailAnalyticsListView.as_view(), name='email_list'),
]