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

    def test_create_product_customer_fail(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Brufen",
            "category": self.category.id,
            "price": 5.00,
            "stock": 50
        }
        response = self.client.post(self.product_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
