import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from historical_sites.models import HistoricalSite

class Command(BaseCommand):
    """Django command to load historical sites from JSON file"""
    
    help = 'Load Irish Civil War historical sites from JSON file'
    
    def add_arguments(self, parser):
        # Optional argument for custom JSON file path
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
                # Convert string date to Python date object
                event_date = datetime.strptime(site_data['date'], '%Y-%m-%d').date()
                
                # Create geographic point from coordinates
                location = Point(site_data['longitude'], site_data['latitude'])
                
                # Map historical period categories to database values
                category_map = {
                    'Easter Rising': 'EASTER_RISING',
                    'War of Independence': 'WAR_INDEPENDENCE',
                    'Treaty Period': 'TREATY',
                    'Civil War': 'CIVIL_WAR',
                    'Civil War End': 'AFTERMATH',
                    'Aftermath': 'AFTERMATH',
                }
                category = category_map.get(site_data['category'], 'CIVIL_WAR')
                
                # Create or update site in database
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
                
                # Log operation status
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
            
            # Display final statistics
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