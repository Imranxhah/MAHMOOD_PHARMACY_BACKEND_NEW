from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Category, Product

User = get_user_model()

class ProductTests(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(email='test@example.com', password='password123', is_active=True)
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password123')
        
        # Create category
        self.category = Category.objects.create(name='Medicine')
        
        # Create product
        self.product = Product.objects.create(
            name='Panadol',
            category=self.category,
            price=10.50,
            stock=100
        )
        
        self.product_url = reverse('product-list') # Assuming router name 'product'

    def test_list_products(self):
        # Allow any
        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Brufen",
            "category": self.category.id,
            "price": 5.00,
            "stock": 50
        }
        response = self.client.post(self.product_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.product_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

from tablib import Dataset
from .resources import ProductResource

class ProductImportTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='ImportCategory')
        self.resource = ProductResource()

    def test_import_new_product_with_barcode(self):
        dataset = Dataset()
        dataset.headers = ['name', 'category', 'price', 'stock', 'barcode']
        dataset.append(['NewItem', 'ImportCategory', '10.00', '100', '123456'])

        result = self.resource.import_data(dataset, dry_run=False)
        self.assertFalse(result.has_errors())
        
        product = Product.objects.get(barcode='123456')
        self.assertEqual(product.name, 'NewItem')
        self.assertEqual(product.stock, 100)

    def test_import_update_existing_by_barcode(self):
        # Create existing product with barcode
        p = Product.objects.create(name='OldName', category=self.category, price=10, stock=50, barcode='999999')
        
        dataset = Dataset()
        dataset.headers = ['name', 'category', 'price', 'stock', 'barcode']
        # Name in file is different, but barcode matches. Should update product.
        dataset.append(['NewNameviaBarcode', 'ImportCategory', '20.00', '10', '999999'])

        result = self.resource.import_data(dataset, dry_run=False)
        self.assertFalse(result.has_errors())
        
        p.refresh_from_db()
        # Expect name to be updated because we verify that Import works (updating fields)
        self.assertEqual(p.name, 'NewNameviaBarcode') 
        
        self.assertEqual(p.stock, 60)
        self.assertEqual(p.price, 20.00)

    def test_import_update_existing_by_name_fallback(self):
        # Create existing product WITHOUT barcode
        p = Product.objects.create(name='Panadol', category=self.category, price=10, stock=50)
        
        dataset = Dataset()
        dataset.headers = ['name', 'category', 'price', 'stock', 'barcode']
        # Barcode in file is empty or missing. Name matches 'Panadol' (case insensitive?). Let's test case insensitive too.
        dataset.append(['panadol', 'ImportCategory', '15.00', '20', ''])

        result = self.resource.import_data(dataset, dry_run=False)
        if result.has_errors():
             print(result.base_errors)
             print(result.row_errors())
        self.assertFalse(result.has_errors())
        
        p.refresh_from_db()
        self.assertEqual(p.stock, 70) # 50 + 20
        self.assertEqual(p.price, 15.00)

    def test_import_empty_barcodes_are_none(self):
        # Two products with empty strings for barcode should be allowed (treated as None)
        dataset = Dataset()
        dataset.headers = ['name', 'category', 'price', 'stock', 'barcode']
        # Use different names to avoid name collision logic
        dataset.append(['Item1', 'ImportCategory', '10', '10', ''])
        dataset.append(['Item2', 'ImportCategory', '10', '10', ''])

        result = self.resource.import_data(dataset, dry_run=False)
        if result.has_errors():
            # Print errors to stdout (will be captured in file)
            print("Row Errors:", result.row_errors())
            for row in result.row_errors():
                print(f"Row {row[0]}: {row[1]}")
                for err in row[1]:
                    print(f"Error: {err.error}")
            print("Base Errors:", result.base_errors)
            
        self.assertFalse(result.has_errors())
        
        self.assertTrue(Product.objects.filter(name='Item1').exists())
        self.assertTrue(Product.objects.filter(name='Item2').exists())
        
        p1 = Product.objects.get(name='Item1')
        p2 = Product.objects.get(name='Item2')
        self.assertIsNone(p1.barcode)
        self.assertIsNone(p2.barcode)

