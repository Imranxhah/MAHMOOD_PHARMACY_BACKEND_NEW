from django.db.models.signals import post_save
from django.dispatch import receiver
from firebase_admin import messaging
from orders.models import Order
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    # Retrieve the user associated with the order
    user = instance.user
    
    # helper to get items string
    items = instance.items.all()
    if items.exists():
        item_str = ", ".join([f"{item.quantity}x {item.product.name}" for item in items])
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
