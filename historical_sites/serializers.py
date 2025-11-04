from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import HistoricalSite

class HistoricalSiteGeoJSONSerializer(GeoFeatureModelSerializer):
    """Serializer for GeoJSON format"""
    
    class Meta:
        model = HistoricalSite
        geo_field = 'location'
        fields = [
            'id', 'name', 'event_date', 'location_name', 
            'category', 'event_type', 'significance', 'casualties'
        ]

class HistoricalSiteDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with all fields"""
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
        return obj.get_latitude()
    
    def get_longitude(self, obj):
        return obj.get_longitude()

class HistoricalSiteListSerializer(serializers.ModelSerializer):
    """Simple serializer for list views"""
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = HistoricalSite
        fields = [
            'id', 'name', 'event_date', 'location_name',
            'latitude', 'longitude', 'category', 'event_type'
        ]
    
    def get_latitude(self, obj):
        return obj.get_latitude()
    
    def get_longitude(self, obj):
        return obj.get_longitude()