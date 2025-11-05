from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint for Docker."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health/', health_check, name='health-check'),  # Docker health check endpoint
    path('', include('historical_sites.urls')),  # Root URL includes historical_sites urls
    path('admin/', admin.site.urls),
    path('api/', include('historical_sites.urls')),  # API endpoints
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
