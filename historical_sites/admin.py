from django.contrib import admin
from .models import HistoricalSite

@admin.register(HistoricalSite)
class HistoricalSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_date', 'category', 'event_type', 'location_name')
    list_filter = ('event_date', 'category', 'event_type', 'created_at')
    search_fields = ('name', 'location_name', 'significance')
    readonly_fields = ('created_at', 'updated_at')
    
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

    
    default_zoom = 7
    default_lon = -6.2603
    default_lat = 53.3498
