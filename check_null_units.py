
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import OrderItem

# Check for nulls
null_units = OrderItem.objects.filter(unit_type__isnull=True).count()
blank_units = OrderItem.objects.filter(unit_type='').count()

print(f"Items with NULL unit_type: {null_units}")
print(f"Items with BLANK unit_type: {blank_units}")

# Check sample
last_item = OrderItem.objects.last()
if last_item:
    print(f"Last Item ID: {last_item.id}, Unit: '{last_item.unit_type}'")
