from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('docs/', RedirectView.as_view(url='/api/docs/', permanent=True), name='docs-redirect'),
    path('swagger/', RedirectView.as_view(url='/api/docs/', permanent=True), name='swagger-redirect'),
    path('api/classifier/', include('classifier.urls')),
    path('api/analytics/', include('analytics.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
