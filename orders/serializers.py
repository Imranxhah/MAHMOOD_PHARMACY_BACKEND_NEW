from rest_framework import serializers
from .models import Order, OrderItem, DeliveryCharge
from products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price_at_purchase']
        read_only_fields = ['price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'branch', 'status', 'payment_method', 'total_amount', 'shipping_address', 'contact_number', 'order_type', 'items', 'created_at']
        read_only_fields = ['user', 'total_amount', 'status']
        depth = 1 # To show full branch details

class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True)
    contact_number = serializers.CharField(required=True)
    branch_id = serializers.IntegerField(required=False)
    payment_method = serializers.ChoiceField(choices=['COD', 'PAYED'], required=False, default='COD')
    order_type = serializers.ChoiceField(choices=['Normal', 'Quick'], required=False, default='Normal')
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    ) 
    # expected items: [{"product_id": 1, "quantity": 2}, ...]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value

class DeliveryChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCharge
        fields = ['amount']
