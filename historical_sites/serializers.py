from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import HistoricalSite
from .models import CountyBoundary


class HistoricalSiteGeoJSONSerializer(GeoFeatureModelSerializer):
    """Converts historical site data to GeoJSON format for map display"""
    
    class Meta:
        model = HistoricalSite
        geo_field = 'location'
        fields = [
            'id', 'name', 'event_date', 'location_name', 
            'category', 'event_type', 'significance', 'casualties'
        ]


class HistoricalSiteDetailSerializer(serializers.ModelSerializer):
    """Provides complete historical site details including computed coordinates"""
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = HistoricalSite
        fields = [
            'id', 'name', 'event_date', 'location_name', 
            'latitude', 'longitude', 'category', 'event_type',
            'significance', 'description', 'casualties',
            'commanders', 'images', 'audio_url', 'sources',
            'created_at', 'updated_at'
        ]
    
    def get_latitude(self, obj):
        """Extracts latitude from location geometry"""
        return obj.get_latitude()
    
    def get_longitude(self, obj):
        """Extracts longitude from location geometry"""
        return obj.get_longitude()


class HistoricalSiteListSerializer(serializers.ModelSerializer):
    """Simplified site data for list views with essential fields"""
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = HistoricalSite
        fields = [
            'id', 'name', 'event_date', 'location_name',
            'latitude', 'longitude', 'category', 'event_type',
            'significance', 'description', 'images', 'casualties'
        ]
    
    def get_latitude(self, obj):
        """Extracts latitude from location geometry"""
        return obj.get_latitude()
    
    def get_longitude(self, obj):
        """Extracts longitude from location geometry"""
        return obj.get_longitude()

    
class CountyBoundarySerializer(GeoFeatureModelSerializer):
    """Serializes county boundary data to GeoJSON format for map overlay"""
    class Meta:
        model = CountyBoundary
        fields = ('id', 'name')
        geo_field = 'geometry'
