import json
import os
from django.core.management.base import BaseCommand
from historical_sites.models import HistoricalSite


class Command(BaseCommand):
    help = 'Update historical sites with descriptions and images from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            nargs='?',
            default='sites_images_descriptions.json',
            help='Path to JSON file containing image and description data'
        )
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'✗ File not found: {json_file}')
            )
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                updates_data = json.load(f)
            
            updated_count = 0
            not_found_count = 0
            
            for update_item in updates_data:
                site_name = update_item.get('name')
                description = update_item.get('description')
                images = update_item.get('images', [])
                
                try:
                    site = HistoricalSite.objects.get(name__iexact=site_name)
                    
                    # Update description and images
                    if description:
                        site.description = description
                    
                    if images:
                        site.images = images
                    
                    site.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Updated: {site.name}'
                        )
                    )
                    updated_count += 1
                    
                except HistoricalSite.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⊘ Site not found: {site_name}'
                        )
                    )
                    not_found_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Update complete!\n'
                    f'  Updated: {updated_count} sites\n'
                    f'  Not found: {not_found_count} sites'
                )
            )
        
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Invalid JSON format: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error updating data: {e}')
            )
