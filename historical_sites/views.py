from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import Distance as D
from django.views.generic import TemplateView
import django_filters
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import CountyBoundary, HistoricalSite
from .serializers import (
    CountyBoundarySerializer,
    HistoricalSiteGeoJSONSerializer,
    HistoricalSiteDetailSerializer,
    HistoricalSiteListSerializer
)



class HistoricalSiteFilter(django_filters.FilterSet):
    """Filter set for Historical Sites with spatial queries"""
    event_date_from = django_filters.DateFilter(field_name='event_date', lookup_expr='gte')
    event_date_to = django_filters.DateFilter(field_name='event_date', lookup_expr='lte')
    county = django_filters.CharFilter(method='filter_by_county')
    
    class Meta:
        model = HistoricalSite
        fields = ['category', 'event_type', 'event_date_from', 'event_date_to', 'county']
    
    def filter_by_county(self, queryset, name, value):
        """Filter sites by county using spatial point-in-polygon queries"""
        if not value:
            return queryset
        
        try:
            county_boundary = CountyBoundary.objects.get(name__iexact=value)
            return queryset.filter(location__within=county_boundary.geometry)
        except CountyBoundary.DoesNotExist:
            return queryset.none()



class HistoricalSiteViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Historical Sites with spatial filtering"""
    queryset = HistoricalSite.objects.all().order_by('event_date')
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = HistoricalSiteFilter
    pagination_class = None
    
    def get_serializer_class(self):
        """Return appropriate serializer based on format"""
        if self.format_kwarg == 'geojson':
            return HistoricalSiteGeoJSONSerializer
        if self.action == 'retrieve':
            return HistoricalSiteDetailSerializer
        return HistoricalSiteListSerializer
    
    @action(detail=False, methods=['post', 'get'])
    def nearby(self, request):
        """Find sites within a specified radius of a point (proximity search)"""
        try:
            if request.method == 'GET':
                latitude = float(request.query_params.get('lat'))
                longitude = float(request.query_params.get('lng'))
                radius_km = float(request.query_params.get('radius_km', 50))
            else:
                latitude = float(request.data.get('lat'))
                longitude = float(request.data.get('lng'))
                radius_km = float(request.data.get('radius_km', 50))
            
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return Response(
                    {'error': 'Invalid coordinates'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if radius_km <= 0 or radius_km > 500:
                return Response(
                    {'error': 'Invalid radius (must be 0-500 km)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_point = Point(longitude, latitude, srid=4326)
            
            nearby_sites = HistoricalSite.objects.filter(
                location__distance_lte=(user_point, D(km=radius_km))
            ).annotate(
                distance=Distance('location', user_point)
            ).order_by('distance')
            
            serializer = self.get_serializer(nearby_sites, many=True)
            
            return Response({
                'count': nearby_sites.count(),
                'radius_km': radius_km,
                'center': {'latitude': latitude, 'longitude': longitude},
                'sites': serializer.data
            })
            
        except (TypeError, ValueError) as e:
            return Response(
                {'error': f'Invalid parameter: {str(e)}'},
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
            'date_range': {'start': start_date, 'end': end_date},
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
    
    @action(detail=False, methods=['post'])
    def in_polygon(self, request):
        """Find sites within a polygon"""
        polygon_coords = request.data.get('polygon')
        try:
            rings = [(lng, lat) for lat, lng in polygon_coords]
            polygon = Polygon(rings)
            sites = HistoricalSite.objects.filter(location__within=polygon)
            return Response({
                'count': sites.count(),
                'sites': self.get_serializer(sites, many=True).data
            })
        except (ValueError, IndexError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


    @action(detail=False, methods=['get'])
    def buffer_zone(self, request):
        """Find sites within buffer zone of another site"""
        site_id = request.query_params.get('site_id')
        buffer_km = float(request.query_params.get('buffer_km', 20))
        
        if buffer_km <= 0 or buffer_km > 100:
            return Response(
                {'error': 'Buffer radius must be 0-100 km'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            center_site = HistoricalSite.objects.get(id=site_id)
            buffer_degrees = buffer_km / 111.0
            buffer_zone = center_site.location.buffer(buffer_degrees)
            
            nearby = HistoricalSite.objects.filter(
                location__within=buffer_zone
            ).exclude(id=site_id).order_by('event_date')
            
            serializer = self.get_serializer(nearby, many=True)
            
            return Response({
                'count': nearby.count(),
                'center_site': center_site.name,
                'center_location': {
                    'latitude': center_site.get_latitude(),
                    'longitude': center_site.get_longitude()
                },
                'buffer_km': buffer_km,
                'sites': serializer.data
            })
        except HistoricalSite.DoesNotExist:
            return Response(
                {'error': 'Site not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except (TypeError, ValueError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



class MapView(TemplateView):
    """Main map view"""
    template_name = 'map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sites'] = HistoricalSite.objects.count()
        context['total_counties'] = CountyBoundary.objects.count()
        return context



class CountyBoundaryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for county boundary polygons (GeoJSON format)"""
    queryset = CountyBoundary.objects.all()
    serializer_class = CountyBoundarySerializer
    pagination_class = None
    
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """Return all county boundaries as GeoJSON FeatureCollection"""
        from django.contrib.gis.serializers import geojson
        counties = self.get_queryset()
        return Response(
            geojson.serialize('geojson', counties, geometry_field='geometry')
        )
    
    @action(detail=False, methods=['get'])
    def geojson_with_colors(self, request):
        """Return county boundaries as GeoJSON FeatureCollection with color properties"""
        import json
        
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#A3E4D7',
            '#F1948A', '#85C1E2', '#F7DC6F', '#D7BDE2', '#A9DFBF',
            '#F8B88B', '#AED6F1', '#F1948A', '#D5A6BD', '#FAD7A0',
            '#85C1E2', '#F7DC6F', '#BB8FCE', '#A9CCE3', '#F8B88B',
            '#F1948A', '#AED6F1'
        ]
        
        counties = self.get_queryset()
        features = []
        
        for idx, county in enumerate(counties):
            geom_json = json.loads(county.geometry.geojson)
            feature = {
                'type': 'Feature',
                'properties': {
                    'name': county.name,
                    'color': colors[idx % len(colors)],
                    'id': county.id
                },
                'geometry': geom_json
            }
            features.append(feature)
        
        return Response({
            'type': 'FeatureCollection',
            'features': features
        })
