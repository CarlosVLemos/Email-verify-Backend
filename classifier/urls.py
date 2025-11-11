from django.urls import path
from . import views

app_name = 'classifier'

urlpatterns = [
    path('', views.EmailClassifierView.as_view(), name='index'),
    path('summary/', views.ExecutiveSummaryView.as_view(), name='executive_summary'),
    path('batch/', views.BatchEmailView.as_view(), name='batch'),
    path('batch/results/', views.BatchResultsView.as_view(), name='batch_results'),
]
