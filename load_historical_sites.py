import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irish_civil_war_project.settings')
django.setup()

from historical_sites.models import HistoricalSite
from django.contrib.gis.geos import Point

sites = [
    ("GPO Occupation - Easter Rising", "1916-04-24", "General Post Office, O'Connell Street, Dublin", "HQ of Easter Rising - precursor to War of Independence", "EASTER_RISING", "Occupation", Point(-6.2605, 53.3493)),
    ("Soloheadbeg Ambush", "1919-01-21", "Soloheadbeg, County Tipperary", "First shots of War of Independence - IRA ambushed RIC escort", "WAR_INDEPENDENCE", "Ambush", Point(-7.8833, 52.5667)),
    ("Bloody Sunday - Croke Park", "1920-11-21", "Croke Park, Dublin", "British forces killed 14 civilians at Gaelic football match", "WAR_INDEPENDENCE", "Massacre", Point(-6.2513, 53.3606)),
    ("Kilmichael Ambush", "1920-11-28", "Kilmichael, County Cork", "IRA flying column killed 17 Auxiliaries - pivotal victory", "WAR_INDEPENDENCE", "Ambush", Point(-9.1333, 51.8167)),
    ("Anglo-Irish Treaty Signing", "1921-12-06", "10 Downing Street, London & Mansion House Dublin", "Treaty signed ending War of Independence, leading to Civil War split", "TREATY", "Political", Point(-6.2603, 53.3439)),
    ("Treaty Ratification", "1922-01-07", "Mansion House, Dublin", "Dáil narrowly approved Treaty (64-57) - led to IRA split", "TREATY", "Political", Point(-6.2586, 53.3421)),
    ("Four Courts Occupation", "1922-04-14", "Four Courts, Inns Quay, Dublin", "Anti-Treaty IRA seized building as HQ - precipitated Civil War", "CIVIL_WAR", "Occupation", Point(-6.2747, 53.3468)),
    ("Bombardment of Four Courts - Civil War Begins", "1922-06-28", "Four Courts, Dublin", "Provisional Government shelled garrison - Public Record Office destroyed", "CIVIL_WAR", "Battle", Point(-6.2747, 53.3468)),
    ("Battle of Dublin Begins", "1922-06-28", "O'Connell Street, Dublin", "Urban fighting - Cathal Brugha killed", "CIVIL_WAR", "Battle", Point(-6.2603, 53.3498)),
    ("Battle of Drogheda", "1922-06-28", "Millmount Fort, Drogheda", "Anti-Treaty seized town, later shelled by Free State", "CIVIL_WAR", "Battle", Point(-6.3528, 53.7175)),
    ("Battle of Limerick", "1922-07-11", "Limerick City (King John's Castle)", "Free State captured city with artillery", "CIVIL_WAR", "Battle", Point(-8.6267, 52.6658)),
    ("Fall of Waterford", "1922-07-19", "Waterford City", "Free State amphibious assault - Republicans evacuated", "CIVIL_WAR", "Battle", Point(-7.1101, 52.2593)),
    ("Battle of Kilmallock", "1922-07-23", "Kilmallock, County Limerick", "Free State took town - end of major conventional fighting", "CIVIL_WAR", "Battle", Point(-8.5667, 52.4)),
    ("Fenit Naval Landing", "1922-08-02", "Fenit Pier, County Kerry", "800 Free State troops landed - outflanked Munster Republic", "CIVIL_WAR", "Landing", Point(-9.8628, 52.2764)),
    ("Battle of Killmallock (Final)", "1922-08-05", "Kilmallock, County Limerick", "2,000 Free State under Eoin O'Duffy - marked conventional war end", "CIVIL_WAR", "Battle", Point(-8.5667, 52.4)),
    ("Cork Landings", "1922-08-08", "Passage West, County Cork", "Seaborne invasions - 16 killed at Rochestown", "CIVIL_WAR", "Battle", Point(-8.3397, 51.8719)),
    ("Fall of Cork City", "1922-08-10", "Cork City", "Republicans evacuated - ended Munster Republic", "CIVIL_WAR", "Surrender", Point(-8.4756, 51.8985)),
    ("Death of Michael Collins", "1922-08-22", "Béal na Bláth, County Cork", "Collins killed in Republican ambush - major turning point", "CIVIL_WAR", "Ambush", Point(-8.8667, 51.8333)),
    ("First Civil War Executions", "1922-11-17", "Kilmainham Gaol, Dublin", "First 4 anti-Treaty IRA executed for arms possession", "CIVIL_WAR", "Execution", Point(-6.3089, 53.3419)),
    ("Mountjoy Executions", "1922-12-08", "Mountjoy Prison, Dublin", "Rory O'Connor, Liam Mellows, Richard Barrett, Joe McKelvey shot in reprisal", "CIVIL_WAR", "Execution", Point(-6.28, 53.3603)),
    ("Death of Liam Lynch", "1923-04-10", "Knockmealdown Mountains, County Tipperary", "Chief of Staff killed - prompted ceasefire", "CIVIL_WAR", "Combat Death", Point(-7.9167, 52.25)),
    ("Ceasefire and Dump Arms Order", "1923-05-24", "Nationwide", "Frank Aiken ordered end to fighting - Republican defeat", "AFTERMATH", "Ceasefire", Point(-6.2603, 53.3498)),
]

# Clear existing data
HistoricalSite.objects.all().delete()

# Load data
for name, date, location_name, significance, category, event_type, point in sites:
    HistoricalSite.objects.create(
        name=name,
        event_date=date,
        location_name=location_name,
        significance=significance,
        category=category,
        event_type=event_type,
        location=point
    )

print(f"Loaded {HistoricalSite.objects.count()} historical sites!")
