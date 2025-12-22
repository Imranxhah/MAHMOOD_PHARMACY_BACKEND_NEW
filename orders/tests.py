from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product
from .models import Order

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123', is_active=True)
        self.category = Category.objects.create(name='Medicine')
        self.product = Product.objects.create(
            name='Panadol',
            category=self.category,
            price=10.00,
            stock=100
        )
        self.orders_url = reverse('order-list')

    def test_create_order(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "shipping_address": "123 Street",
            "contact_number": "1234567890",
            "items": [
                {"product_id": self.product.id, "quantity": 2}
            ]
        }
        response = self.client.post(self.orders_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        
        # Verify stock deduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 98)

    def test_create_order_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "shipping_address": "123 Street",
            "contact_number": "1234567890",
            "items": [
                {"product_id": self.product.id, "quantity": 101}
            ]
        }
        response = self.client.post(self.orders_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_quick_order(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quick-order')
        data = {
            "product_id": self.product.id,
            "quantity": 1,
            "shipping_address": "Quick Addr"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
