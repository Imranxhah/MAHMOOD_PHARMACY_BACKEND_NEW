from django.core.management.base import BaseCommand
from branches.models import Branch

class Command(BaseCommand):
    help = 'Seeds dummy branches'

    def handle(self, *args, **kwargs):
        branches = [
            {"name": "Main Branch", "lat": 33.6844, "long": 73.0479, "address": "Blue Area, Islamabad"},
            {"name": "Saddar Branch", "lat": 33.5651, "long": 73.0169, "address": "Saddar, Rawalpindi"},
            {"name": "F-10 Markaz", "lat": 33.7114, "long": 73.0076, "address": "F-10, Islamabad"},
        ]
        
        for b in branches:
            branch, created = Branch.objects.get_or_create(
                name=b['name'],
                defaults={
                    'latitude': b['lat'],
                    'longitude': b['long'],
                    'address': b['address'],
                    'phone': '051-1234567'
                }
            )
            if created:
                self.stdout.write(f"Created {b['name']}")
            else:
                self.stdout.write(f"Exists {b['name']}")
