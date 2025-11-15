from django.urls import path
from .views import (
    EmailClassifierAPIView, 
    ExecutiveSummaryAPIView, 
    BatchEmailAPIView, 
    HealthCheckAPIView,
    HuggingFaceResponseAPIView
)
app_name = 'classifier'
urlpatterns = [
    path('classify/', EmailClassifierAPIView.as_view(), name='classify'),
    path('summary/', ExecutiveSummaryAPIView.as_view(), name='summary'),
    path('batch/', BatchEmailAPIView.as_view(), name='batch'),
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    path('huggingface-response/', HuggingFaceResponseAPIView.as_view(), name='huggingface-response'),
]
