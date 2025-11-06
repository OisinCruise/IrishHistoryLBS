from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sites', views.HistoricalSiteViewSet, basename='site')
router.register(r'county-boundaries', views.CountyBoundaryViewSet, basename='county-boundary')

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('', include(router.urls)),  
]
