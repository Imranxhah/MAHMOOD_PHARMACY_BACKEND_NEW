
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Category, Product
from rest_framework.test import APIRequestFactory
from products.views import ProductViewSet

def test_related_products_filter():
    # 1. Setup Data
    cat = Category.objects.create(name="Test Category")
    
    p1 = Product.objects.create(name="P1", category=cat, price=10, generic_name="GenA", stock=10)
    p2 = Product.objects.create(name="P2", category=cat, price=10, generic_name="GenA", stock=10)
    p3 = Product.objects.create(name="P3", category=cat, price=10, generic_name="GenB", stock=10)
    
    print(f"Created products: {p1.name}({p1.generic_name}), {p2.name}({p2.generic_name}), {p3.name}({p3.generic_name})", flush=True)

    # 2. Test Only Category Filter
    factory = APIRequestFactory()
    view = ProductViewSet.as_view({'get': 'list'})
    
    req_cat = factory.get('/api/products/', {'category': cat.id})
    res_cat = view(req_cat)
    print("\nRequest: ?category=" + str(cat.id), flush=True)
    print("Result count:", len(res_cat.data['results']), flush=True)
    print("Results:", [p['name'] for p in res_cat.data['results']], flush=True)
    
    # 3. Test Category AND Generic Name Filter
    req_gen = factory.get('/api/products/', {'category': cat.id, 'generic_name': 'GenA'})
    res_gen = view(req_gen)
    print("\nRequest: ?category=" + str(cat.id) + "&generic_name=GenA", flush=True)
    print("Result count:", len(res_gen.data['results']), flush=True)
    print("Results:", [p['name'] for p in res_gen.data['results']], flush=True)

    # Cleanup
    p1.delete()
    p2.delete()
    p3.delete()
    cat.delete()

if __name__ == "__main__":
    test_related_products_filter()
