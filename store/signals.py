from email import message
from itertools import product
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Cart, CartItem, Order, OrderItem, Notification, Customer

@receiver(post_save, sender=Cart)
def cart_created(sender, instance, created, **kwargs):
    """Send notification if a new cart created
    
    Args:
        sender (Cart): The sender of the signal.
        instance (Cart): The instance of the signal.
        created (bool): Whether the instance is created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f'Your cart has been created: {instance.uid}',
            is_admin=False
        )

@receiver(post_save, sender=CartItem)
def cart_item_changed(sender, instance, created, **kwargs):
    """Send notification if a cart item changed
    
    Args:
        sender (CartItem): The sender of the signal.
        instance (CartItem): The instance of the signal.
        created (bool): Whether the instance is created.
        **kwargs: Additional keyword arguments.
    """
    cart = instance.cart
    product = instance.product

    if created:
        message = f'Product {product.title} has been added to your cart.'
    else:
        message = f'Quantity of product {product.title} has been changed to {instance.quantity}. '
    
    Notification.objects.create(
        user=cart.user,
        message=message,
        is_admin=False
    )

@receiver(post_delete, sender=CartItem)
def cart_item_removed(sender, instance, **kwargs):
    """Send notification if a cart item removed"""
    try:
        cart = instance.cart
        product = instance.product

        message = f'Product {product.title} has been removed from your cart.'
        
        Notification.objects.create(
            user=cart.user,
            message=message,
            is_admin=False
        )
    except (Cart.DoesNotExist, AttributeError):
        # Cart might have been deleted already
        pass

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Send notification when an order is created or if order status changed"""
    if instance.pk and created:
        if instance.payment_status == Order.PAYMENT_STATUS_COMPLETE:
            Notification.objects.create(
                user=instance.user,
                message=f'Your order {instance.pk} has been paid.',
                is_admin=False
            )
        elif instance.payment_status == Order.PAYMENT_STATUS_FAILED:
            Notification.objects.create(
                user=instance.user,
                message=f'Your order {instance.pk} has failed.',
                is_admin=False
            )
        elif instance.payment_status == Order.PAYMENT_STATUS_PENDING:
            Notification.objects.create(
                user=instance.user,
                message=f'Your order {instance.pk} is pending.',
                is_admin=False
            )

    user = instance.user

    if created:
        message = f"Your order #{instance.pk} has been placed successfully."
    else:
        message = f"Your order #{instance.pk} has been updated to {instance.get_payment_status_display()}."
    
    Notification.objects.create(
        user=user,
        message=message,
        is_admin=True # This is from admin/sytem notifications
    )

@receiver(post_save, sender=OrderItem)
def order_item_added(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        product = instance.product
        message = f'Product {product.title} has been added to your order.'
        Notification.objects.create(
            user=instance.user,
            message=message,
            is_admin=True
        )
