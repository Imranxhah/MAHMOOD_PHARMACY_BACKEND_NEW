from django.test import TestCase
from products.models import Product, Category
from orders.models import Order, OrderItem, DeliveryCharge
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class OrderPricingLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password', mobile='03001234567')
        self.category = Category.objects.create(name='Meds')
        self.product = Product.objects.create(
            name='Panadol',
            category=self.category,
            price=10.00,       # Unit Price
            pack_price=100.00, # Pack Price (10x cheap?)
            strip_price=12.00, # Strip Price
            strips_in_pack=10,
            tablets_in_strip=10,
            stock=100 # 100 Strips
        )
        self.delivery_charge = DeliveryCharge.objects.create(amount=50.00)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_api_order_total_includes_delivery_and_pack_price(self):
        """
        Test that creating an order via API with 'Pack' unit type:
        1. Uses pack_price (100.00)
        2. Adds delivery charge (50.00)
        Total should be 150.00
        """
        payload = {
            "shipping_address": "Home",
            "contact_number": "03001234567",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "unit_type": "Pack"
                }
            ]
        }
        response = self.client.post('/api/orders/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        
        # Expected: 1 * 100.00 (Pack) + 50.00 (Delivery) = 150.00
        self.assertEqual(float(order.total_amount), 150.00)
        
        # Check Item Price
        item = order.items.first()
        self.assertEqual(float(item.price_at_purchase), 100.00)
        self.assertEqual(item.unit_type, 'Pack')

    def test_admin_model_save_logic(self):
        """
        Test that creating an OrderItem directly (like Admin does) with 'Pack':
        1. Automatically sets price_at_purchase to pack_price if blank.
        2. Signal updates Order total including delivery.
        """
        order = Order.objects.create(user=self.user, total_amount=0)
        
        # Simulate Admin creating item: unit_type='Pack', price left blank
        item = OrderItem(
            order=order,
            product=self.product,
            quantity=1,
            unit_type='Pack'
        )
        item.save() # Should trigger logic in save() to set price
        
        item.refresh_from_db()
        # Expectation: save() logic should check unit_type and use pack_price
        self.assertEqual(float(item.price_at_purchase), 100.00) 
        
        # Verify Signal updated Order Total
        order.refresh_from_db()
        # 100 (Item) + 50 (Delivery) = 150
        # 100 (Item) + 50 (Delivery) = 150
        self.assertEqual(float(order.total_amount), 150.00)

    def test_admin_form_post_saves_correct_price_and_total(self):
        """
        Simulate a POST request from the Admin panel where the user (via JS) 
        has set a Pack Price. Verify that this specific price is respected 
        and the Order Total matches.
        """
        # Create a new order
        order = Order.objects.create(user=self.user, status='Pending')
        
        # Define the manual price (Pack Price) the JS would have set
        manual_pack_price = self.product.pack_price # 100.00
        
        # Create an OrderItem directly to simulate saving the form data
        # In a real Admin POST, this would be validated and saved.
        # We manually save one with the 'Pack' price to ensure the model logic DOES NOT override it
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            unit_type='Pack',
            quantity=1,
            price_at_purchase=manual_pack_price
        )
        
        # Verify the item saved the correct manual price, not the default Unit price or anything else
        item.refresh_from_db()
        self.assertEqual(float(item.price_at_purchase), 100.00, "Model should save the manually provided Pack Price")
        
        # Verify Order Total
        # Total = (1 * 100) + 50 (Delivery) = 150
        expected_total = float(manual_pack_price + self.delivery_charge.amount)
        order.refresh_from_db()
        self.assertEqual(float(order.total_amount), expected_total, "Order Total should include Pack Price + Delivery Charge")
