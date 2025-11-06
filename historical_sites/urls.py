from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize DRF router
router = DefaultRouter()
# Register viewsets with router
router.register(r'sites', views.HistoricalSiteViewSet, basename='site')
router.register(r'county-boundaries', views.CountyBoundaryViewSet, basename='county-boundary')

# Define URL patterns
urlpatterns = [
    path('', views.MapView.as_view(), name='map'),  # Main map view
    path('', include(router.urls)),  # Include API endpoints
]
