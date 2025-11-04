# Irish Civil War LBS - Database Schema Documentation

## Overview

The Irish Civil War Location-Based Services application uses **PostgreSQL with PostGIS** and Django GIS models to store and query historical site information. This schema derives directly from your `historical_sites/models.py` source.

## Historical Sites Table (`historicalsite`)

### Model Definition (Django ORM)

```python
from django.contrib.gis.db import models

class HistoricalSite(models.Model):
    CATEGORY_CHOICES = [
        ('EASTER_RISING', 'Easter Rising (1916)'),
        ('WAR_INDEPENDENCE', 'War of Independence (1919-1921)'),
        ('TREATY', 'Treaty Period (1921-1922)'),
        ('CIVIL_WAR', 'Civil War (1922-1923)'),
        ('AFTERMATH', 'Aftermath & Establishment (1923+)'),
    ]
    name = models.CharField(max_length=255, unique=True)
    event_date = models.DateField()
    location_name = models.CharField(max_length=500)
    location = models.PointField(srid=4326, help_text="WGS84 coordinates (Longitude, Latitude)")
    significance = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    event_type = models.CharField(max_length=100, help_text="e.g., Battle, Ambush, Execution, Political")
    description = models.TextField(blank=True, null=True)
    casualties = models.IntegerField(null=True, blank=True)
    commanders = models.JSONField(blank=True, null=True, default=list)
    images = models.JSONField(blank=True, null=True, default=list)
    audio_url = models.URLField(blank=True, null=True)
    sources = models.JSONField(blank=True, null=True, default=list)
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
```

## Field Descriptions

| Field | Type | Constraints/Choices | Description |
|-------|------|-------------------|-------------|
| name | CharField(255), unique | NOT NULL/unique | Human-readable site name |
| event_date | DateField | NOT NULL | Date of the historical event |
| location_name | CharField(500) | NOT NULL | Name of the physical location |
| location | PointField(srid=4326) | NOT NULL | WGS84 Point geometry (lon, lat) |
| significance | TextField | NOT NULL | Historical importance/context |
| category | CharField(50) | CATEGORY_CHOICES | Event category |
| event_type | CharField(100) | NOT NULL | Event type (battle, ambush...) |
| description | TextField | blank/null | Extended narrative |
| casualties | IntegerField | blank/null | Number of casualties |
| commanders | JSONField | blank/null | List of commanders |
| images | JSONField | blank/null | Related images |
| audio_url | URLField | blank/null | Related audio |
| sources | JSONField | blank/null | Source references |
| created_at | DateTimeField | auto-now-add | Creation timestamp |
| updated_at | DateTimeField | auto-now | Last updated timestamp |

### Choices
**category**:
- `EASTER_RISING`: Easter Rising (1916)
- `WAR_INDEPENDENCE`: War of Independence (1919-1921)
- `TREATY`: Treaty Period (1921-1922)
- `CIVIL_WAR`: Civil War (1922-1923)
- `AFTERMATH`: Aftermath & Establishment (1923+)

## Indexes

- Index on `event_date` field
- Index on `category` field

## Metadata

- Ordering on `event_date` and `name`
