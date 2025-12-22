from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('PAYED', 'Payed'),
    )

    ORDER_TYPE_CHOICES = (
        ('Normal', 'Normal'),
        ('Quick', 'Quick'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    branch = models.ForeignKey('branches.Branch', related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Order Status")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD', verbose_name="Payment Method")
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='Normal')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.TextField()
    contact_number = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^03\d{9}$',
                message="Phone number must be 11 digits and start with 03 (e.g., 03XXXXXXXXX) with no spaces or characters."
            )
        ],
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT) # Protect product from deletion if in order
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) # Store price at time of purchase

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class DeliveryCharge(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Delivery charges amount (e.g. 150.00)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery Charges: {self.amount}"

    class Meta:
        verbose_name_plural = "Delivery Charges"
