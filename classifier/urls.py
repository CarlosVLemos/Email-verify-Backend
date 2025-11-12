from django.urls import path
from .views import EmailClassifierAPIView, ExecutiveSummaryAPIView, BatchEmailAPIView, HealthCheckAPIView

app_name = 'classifier'

urlpatterns = [
    path('classify/', EmailClassifierAPIView.as_view(), name='classify'),
    path('summary/', ExecutiveSummaryAPIView.as_view(), name='summary'),
    path('batch/', BatchEmailAPIView.as_view(), name='batch'),
    path('health/', HealthCheckAPIView.as_view(), name='health'),
]
