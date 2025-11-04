from django.contrib.gis.db import models
from django.utils import timezone

class HistoricalSite(models.Model):
    """Model representing a historical site related to Irish Civil War"""
    
    CATEGORY_CHOICES = [
        ('EASTER_RISING', 'Easter Rising (1916)'),
        ('WAR_INDEPENDENCE', 'War of Independence (1919-1921)'),
        ('TREATY', 'Treaty Period (1921-1922)'),
        ('CIVIL_WAR', 'Civil War (1922-1923)'),
        ('AFTERMATH', 'Aftermath & Establishment (1923+)'),
    ]
    
    # Basic information
    name = models.CharField(max_length=255, unique=True)
    event_date = models.DateField()
    location_name = models.CharField(max_length=500)
    
    # Spatial data (Point geometry)
    location = models.PointField(srid=4326, help_text="WGS84 coordinates (Longitude, Latitude)")
    
    # Historical context
    significance = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    event_type = models.CharField(max_length=100, help_text="e.g., Battle, Ambush, Execution, Political")
    
    # Additional details
    description = models.TextField(blank=True, null=True)
    casualties = models.IntegerField(null=True, blank=True)
    commanders = models.JSONField(blank=True, null=True, default=list)
    
    # Media and resources
    images = models.JSONField(blank=True, null=True, default=list)
    audio_url = models.URLField(blank=True, null=True)
    sources = models.JSONField(blank=True, null=True, default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['event_date', 'name']
        indexes = [
            models.Index(fields=['event_date']),
            models.Index(fields=['category']),
        ]
        verbose_name = 'Historical Site'
        verbose_name_plural = 'Historical Sites'
    
    def __str__(self):
        return f"{self.name} ({self.event_date.year})"
    
    def get_latitude(self):
        """Return latitude coordinate"""
        return self.location.y
    
    def get_longitude(self):
        """Return longitude coordinate"""
        return self.location.x