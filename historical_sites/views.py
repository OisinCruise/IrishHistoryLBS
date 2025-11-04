from rest_framework import viewsets, status
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.measure import Distance as D
from django.contrib.gis.db.models.functions import Distance  
from django.contrib.gis.geos import Point
from django_filters import rest_framework as filters
from .models import HistoricalSite
from .serializers import (
    HistoricalSiteGeoJSONSerializer,
    HistoricalSiteDetailSerializer,
    HistoricalSiteListSerializer
)


class HistoricalSiteFilter(filters.FilterSet):
    event_date_from = filters.DateFilter(field_name='event_date', lookup_expr='gte')
    event_date_to = filters.DateFilter(field_name='event_date', lookup_expr='lte')
    
    class Meta:
        model = HistoricalSite
        fields = ['category', 'event_type', 'event_date_from', 'event_date_to']


class HistoricalSiteViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Historical Sites"""
    queryset = HistoricalSite.objects.all().order_by('event_date')
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = HistoricalSiteFilter
    pagination_class = None
    
    def get_serializer_class(self):
        if self.format_kwarg == 'geojson':
            return HistoricalSiteGeoJSONSerializer
        if self.action == 'retrieve':
            return HistoricalSiteDetailSerializer
        return HistoricalSiteListSerializer
    
    @action(detail=False, methods=['post', 'get'])
    def nearby(self, request):
        """Find sites within a specified radius"""
        try:
            # Handle GET requests
            if request.method == 'GET':
                latitude = float(request.query_params.get('lat'))
                longitude = float(request.query_params.get('lng'))
                radius_km = float(request.query_params.get('radius_km', 50))
            # Handle POST requests 
            else:
                latitude = float(request.data.get('lat'))
                longitude = float(request.data.get('lng'))
                radius_km = float(request.data.get('radius_km', 50))
            
            # Validate inputs
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return Response(
                    {'error': 'Invalid coordinates. Latitude must be -90 to 90, Longitude -180 to 180'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if radius_km <= 0 or radius_km > 500:
                return Response(
                    {'error': 'Invalid radius. Must be between 0 and 500 km'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create point and perform spatial query
            user_point = Point(longitude, latitude, srid=4326)
            
            nearby_sites = HistoricalSite.objects.filter(
                location__distance_lte=(user_point, D(km=radius_km))
            ).annotate(
                distance=Distance('location', user_point)
            ).order_by('distance')
            
            # Serialize results
            serializer = self.get_serializer(nearby_sites, many=True)
            
            return Response({
                'count': nearby_sites.count(),
                'radius_km': radius_km,
                'center': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'sites': serializer.data
            })
            
        except (TypeError, ValueError, AttributeError) as e:
            return Response(
                {'error': f'Invalid parameters: {str(e)}. Required: lat, lng, radius_km'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get sites within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(event_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(event_date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'date_range': {
                'start': start_date or 'N/A',
                'end': end_date or 'N/A'
            },
            'sites': serializer.data
        })

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available categories with counts"""
        categories = {}
        for site in self.get_queryset():
            cat = site.get_category_display()
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        return Response(categories)


class MapView(TemplateView):
    """Main map view"""
    template_name = 'map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sites'] = HistoricalSite.objects.count()
        return context
