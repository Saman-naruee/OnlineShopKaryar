from ast import mod
from attr import validate
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models  
from mptt.models import MPTTModel, TreeForeignKey  
from core.models import User
from .validators import validate_image_size
from django.core.exceptions import ValidationError
# import pillow


class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, default='')
    discount = models.FloatField(default=0)

    def __str__(self) -> str:
        return str(self.discount)


class Collection(MPTTModel):
    title = models.CharField(max_length=255, unique=True)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_in_collections')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    attributes_schema = models.JSONField(default=dict)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if Collection.objects.filter(title=self.title).exists():
            raise ValidationError('Collection with this title already exists.')
        super().save(*args, **kwargs)

class Product(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.PositiveBigIntegerField()
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if Product.objects.filter(title=self.title).exists():
            raise ValidationError('Product with this title already exists.')
        super().save(*args, **kwargs)

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='media/products',
        validators=[validate_image_size]
        )

class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]

    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    def __str__(self) -> str:
        return f"Mr.{self.username}"
    
    class Meta:
        permissions = [
            ('view_history', 'Can View History')
        ]


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f'{self.pk}.Order of {self.customer}'
    
    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel orders')
        ]
 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.customer}: {self.city}'
import uuid
class Cart(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='carts')

    def __str__(self) -> str:
        return str(self.created_at)


class CartItem(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'product']]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reveiws')
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # A User can only leave one review for a product.
        if Review.objects.filter(product_id=self.product_id, user_id=self.user_id).exists():
            raise ValidationError('A user can only leave one review for a product.')
        super().save(*args, **kwargs)


class Notification(models.Model):
    READING_STATUS = [
        ('S', 'Readed'), 
        ('U', 'Unread')
    ]

    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False) # if user is admin
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=READING_STATUS, default='U')

    def __str__(self) -> str:
        return f'{self.message} - {self.user.user.username}'
