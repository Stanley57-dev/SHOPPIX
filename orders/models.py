
import uuid

from django.conf import settings
from django.db import models
from products.models import Product
from decimal import Decimal


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    DELIVERY_DATE_STATUS_CHOICES = [
    ('pending', 'Awaiting Confirmation'),
    ('confirmed', 'Confirmed'),
    ('changed', 'Changed by Shopora'),
  ]

    order_number = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    delivery_fee = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=Decimal('0.00')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    estimated_delivery_date = models.DateField(
    null=True,
    blank=True
    )

    requested_delivery_date = models.DateField(
    null=True,
    blank=True
   )

    requested_delivery_status = models.CharField(
    max_length=20,
    choices=DELIVERY_DATE_STATUS_CHOICES,
    default='pending'
   )

    actual_delivery_date = models.DateField(
    null=True,
    blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    product_name = models.CharField(max_length=200)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

@property
def subtotal(self):
    if self.price is None:
        return 0
    return self.price * self.quantity