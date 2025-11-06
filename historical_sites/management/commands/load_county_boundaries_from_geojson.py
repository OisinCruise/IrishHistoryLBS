import json
import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from historical_sites.models import CountyBoundary


class Command(BaseCommand):
    help = 'Load Irish county boundaries from GeoJSON with proper coordinate transformation'
    
    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to GeoJSON file')
    
    def handle(self, *args, **options):
        geojson_file = options['geojson_file']
        
        if not os.path.exists(geojson_file):
            self.stdout.write(self.style.ERROR(f'✗ File not found: {geojson_file}'))
            return
        
        self.stdout.write(f"Loading county boundaries from {geojson_file}...")
        
        try:
            with open(geojson_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'✗ Invalid JSON: {str(e)}'))
            return
        
        features = data.get('features', [])
        self.stdout.write(f"Found {len(features)} features")
        
        processed_counties = set()
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for idx, feature in enumerate(features):
            try:
                props = feature.get('properties', {})
                geom = feature.get('geometry')
                
                if not geom:
                    skipped_count += 1
                    continue
                
                # Extract county name
                county_name = (props.get('COUNTY') or props.get('county') or 
                              props.get('NAME') or props.get('name'))
                
                if not county_name:
                    skipped_count += 1
                    continue
                
                county_name = county_name.strip().upper()
                
                # Skip duplicates in this load
                if county_name in processed_counties:
                    self.stdout.write(self.style.WARNING(f'⊘ Duplicate in file: {county_name}'))
                    skipped_count += 1
                    continue
                
                processed_counties.add(county_name)
                
                # Load geometry from GeoJSON - DO NOT set SRID yet (to avoid conflict)
                geom_geojson = json.dumps(geom)
                
                try:
                    # Create geometry WITHOUT SRID first
                    geometry = GEOSGeometry(geom_geojson)
                    
                    # Strip any existing SRID that came from GeoJSON
                    geometry.srid = None
                    
                    # NOW set SRID to EPSG:2157 (Irish Grid)
                    geometry.srid = 2157
                    
                    # Transform from EPSG:2157 to EPSG:4326 (WGS84)
                    geometry.transform(4326)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'⚠ Transformed {county_name} from EPSG:2157 to EPSG:4326'
                    ))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'✗ Failed to parse/transform geometry for {county_name}: {str(e)}'
                    ))
                    skipped_count += 1
                    continue
                
                # Validate geometry
                if not geometry.valid:
                    self.stdout.write(self.style.ERROR(f'✗ Invalid geometry for {county_name}'))
                    skipped_count += 1
                    continue
                
                # Validate final coordinates are in Ireland range (WGS84)
                centroid = geometry.centroid
                if not (-11 < centroid.x < -5 and 51 < centroid.y < 56):
                    self.stdout.write(self.style.ERROR(
                        f'✗ Invalid location after transform for {county_name}: {centroid}'
                    ))
                    skipped_count += 1
                    continue
                
                # Create or update the county
                county, is_created = CountyBoundary.objects.update_or_create(
                    name=county_name,
                    defaults={'geometry': geometry}
                )
                
                if is_created:
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created: {county_name} (centroid: {centroid.x:.4f}, {centroid.y:.4f})'
                    ))
                    created_count += 1
                else:
                    self.stdout.write(self.style.HTTP_INFO(
                        f'⟳ Updated: {county_name} (centroid: {centroid.x:.4f}, {centroid.y:.4f})'
                    ))
                    updated_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error at feature {idx}: {str(e)}'))
                import traceback
                traceback.print_exc()
                skipped_count += 1
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(
            f'✓ Successfully processed {created_count + updated_count} counties!'
        ))
        self.stdout.write(f'  • Created: {created_count}')
        self.stdout.write(f'  • Updated: {updated_count}')
        self.stdout.write(f'  • Skipped: {skipped_count}')
        self.stdout.write("="*60)
        
        # Verify samples
        if created_count + updated_count > 0:
            self.stdout.write("\nVerification (first 3 counties):")
            for county in CountyBoundary.objects.all()[:3]:
                centroid = county.geometry.centroid
                self.stdout.write(
                    f"  • {county.name}: SRID={county.geometry.srid}, "
                    f"Centroid=({centroid.x:.4f}, {centroid.y:.4f})"
                )
