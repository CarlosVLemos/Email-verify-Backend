from django.urls import path
from . import views

app_name = 'classifier'

urlpatterns = [
    path('', views.EmailClassifierView.as_view(), name='index'),
]
