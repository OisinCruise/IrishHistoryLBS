import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from historical_sites.models import HistoricalSite

class Command(BaseCommand):
    help = 'Load Irish Civil War historical sites from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            nargs='?',
            default='irish_civil_war_sites.json',
            help='Path to JSON file containing site data'
        )
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'File not found: {json_file}')
            )
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sites_data = json.load(f)
            
            created_count = 0
            updated_count = 0
            
            for site_data in sites_data:
                # Parse date
                event_date = datetime.strptime(site_data['date'], '%Y-%m-%d').date()
                
                # Create Point geometry (longitude, latitude)
                location = Point(site_data['longitude'], site_data['latitude'])
                
                # Map category from string to database value
                category_map = {
                    'Easter Rising': 'EASTER_RISING',
                    'War of Independence': 'WAR_INDEPENDENCE',
                    'Treaty Period': 'TREATY',
                    'Civil War': 'CIVIL_WAR',
                    'Civil War End': 'AFTERMATH',
                    'Aftermath': 'AFTERMATH',
                }
                category = category_map.get(site_data['category'], 'CIVIL_WAR')
                
                # Get or create the site
                site, created = HistoricalSite.objects.update_or_create(
                    name=site_data['event'],
                    defaults={
                        'event_date': event_date,
                        'location_name': site_data['location'],
                        'location': location,
                        'significance': site_data['significance'],
                        'category': category,
                        'event_type': site_data['type'],
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {site.name}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⟳ Updated: {site.name}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Data loading complete!\n'
                    f'  Created: {created_count} sites\n'
                    f'  Updated: {updated_count} sites\n'
                    f'  Total: {HistoricalSite.objects.count()} sites in database'
                )
            )
        
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON format: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading data: {e}')
            )