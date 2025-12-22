from django.core.management.base import BaseCommand
from products.models import Category, Product
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seeds the database with dummy products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        categories_data = [
            'Medicines',
            'Healthcare',
            'Baby Care',
            'Personal Care',
            'Devices'
        ]

        categories = {}
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_name)
            categories[cat_name] = cat
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        products_data = [
            {'name': 'Panadol Extra', 'price': 50.00, 'cat': 'Medicines', 'desc': 'Effective for fever and pain relief.'},
            {'name': 'Brufen 400mg', 'price': 120.00, 'cat': 'Medicines', 'desc': 'Anti-inflammatory pain killer.'},
            {'name': 'Disprin', 'price': 20.00, 'cat': 'Medicines', 'desc': 'Fast relief from headache.'},
            {'name': 'Dettol Antiseptic', 'price': 450.00, 'cat': 'Healthcare', 'desc': 'Kills 99.9% of germs.'},
            {'name': 'Band-Aid', 'price': 50.00, 'cat': 'Healthcare', 'desc': 'Waterproof adhesive bandages.'},
            {'name': 'Pampers Size 1', 'price': 1500.00, 'cat': 'Baby Care', 'desc': 'Comfortable diapers for newborns.'},
            {'name': 'Johnson Baby Oil', 'price': 350.00, 'cat': 'Baby Care', 'desc': 'Gentle massage oil.'},
            {'name': 'Nivea Men Face Wash', 'price': 400.00, 'cat': 'Personal Care', 'desc': 'Deep cleaning face wash.'},
            {'name': 'Sunsilk Shampoo', 'price': 320.00, 'cat': 'Personal Care', 'desc': 'For soft and silky hair.'},
            {'name': 'B.P Monitor Digital', 'price': 2500.00, 'cat': 'Devices', 'desc': 'Automatic blood pressure monitor.'},
        ]

        for p in products_data:
            product, created = Product.objects.get_or_create(
                name=p['name'],
                defaults={
                    'category': categories[p['cat']],
                    'price': Decimal(p['price']),
                    'stock': random.randint(10, 100),
                    'description': p['desc'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created product: {p["name"]}')
            else:
                self.stdout.write(f'Product already exists: {p["name"]}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded database.'))
