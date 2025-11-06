from django.contrib import admin
from .models import HistoricalSite

@admin.register(HistoricalSite)
class HistoricalSiteAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for managing Historical Sites.
    Provides organized fieldsets and filtering options for site management.
    """
    
    # Configure displayed columns in the sites list
    list_display = ('name', 'event_date', 'category', 'event_type', 'location_name')
    
    # Add filtering options in the right sidebar
    list_filter = ('event_date', 'category', 'event_type', 'created_at')
    
    # Enable search functionality for key fields
    search_fields = ('name', 'location_name', 'significance')
    
    # Prevent modification of timestamp fields
    readonly_fields = ('created_at', 'updated_at')
    
    # Organize fields into logical groupings
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'event_date', 'location_name', 'location')
        }),
        ('Classification', {
            'fields': ('category', 'event_type')
        }),
        ('Historical Context', {
            'fields': ('significance', 'description', 'casualties', 'commanders')
        }),
        ('Media & Resources', {
            'fields': ('images', 'audio_url', 'sources')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Default map center coordinates for Ireland
    default_zoom = 7
    default_lon = -6.2603  # Dublin longitude
    default_lat = 53.3498  # Dublin latitude