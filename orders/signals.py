
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.db import models
from orders.models import Order, OrderItem
from notifications.models import Notification
import logging

# Firebase import (assumed available based on user's code)
try:
    from firebase_admin import messaging
except ImportError:
    pass # Handle if firebase_admin is not installed locally

logger = logging.getLogger(__name__)

# --- 1. Notification Logic (Restored from your existing code) ---
@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    # Retrieve the user associated with the order
    user = instance.user
    
    # helper to get items string
    items = instance.items.all()
    if items.exists():
        item_str = ", ".join([f"{item.quantity} {item.unit_type} of {item.product.name}" for item in items])
    else:
        item_str = ""

    # Check if user has a registered device (FCM Token)
    # We will log the flow regardless of token existence for debugging
    
    if created:
        # If created with no items, it's likely the first step of the view transaction.
        # We skip this and wait for the second save which updates total_amount after adding items.
        if not item_str:
            logger.info(f"Order #{instance.id} created but has no items yet. Skipping notification.")
            return

        title = "Order Placed"
        body = f"Your order #{instance.id} has been placed. Items: {item_str}"
    else:
        # Order Update (or the second save of creation)
        if instance.status == 'Pending' and item_str:
            # This handles the second save after items are added
            title = "Order Placed"
            body = f"Your order #{instance.id} has been placed successfully. Items: {item_str}"
        else:
            title = "Order Update"
            body = f"Your order #{instance.id} is now {instance.status}. Items: {item_str}"

    # Always attempt to save DB notification

    # Create DB Entry
    # This creation will trigger the 'post_save' signal in notifications/signals.py
    # which will handle the actual Firebase Push.
    try:
        Notification.objects.create(user=user, title=title, body=body, order=instance)
    except Exception as e:
        # Fallback print/log if notification creation fails
        print(f"Error creating notification object: {e}")


# --- 2. Auto-Total Calculation (New Feature) ---
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    # Safely get order_id (instance.order might trigger DB lookup failing if order is deleted)
    order_id = instance.order_id
    
    # Check if Order still exists (It might be deleted in a cascade)
    # If we are deleting the Order, the OrderItems are deleted, causing this signal.
    # accessing the Order blindly and saving it would cause a crash or resurrect it.
    if not Order.objects.filter(pk=order_id).exists():
        return

    try:
        order = Order.objects.get(pk=order_id)
        # Calculate sum of all items in the order
        total = order.items.aggregate(
            total=Sum(models.F('price_at_purchase') * models.F('quantity'))
        )['total'] or 0
        
        # Add Delivery Charge
        from .models import DeliveryCharge
        delivery_charge = DeliveryCharge.objects.first()
        if delivery_charge:
            total += delivery_charge.amount

        # Update the order's total_amount safely without triggering post_save signals
        # This prevents creating new "Notification" objects during a delete cascade,
        # which would otherwise block the deletion with an IntegrityError.
        Order.objects.filter(pk=order_id).update(total_amount=total)
        
    except Order.DoesNotExist:
        # Should be caught by the filter check above, but safely pass just in case
        pass
    except Exception as e:
        logger.error(f"Error updating order total for order {order_id}: {e}")
