from django.db import models

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    start_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField()

class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(default='-')
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=6)
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, 
        )
    promotions = models.ManyToManyField(Promotion)


class Customer(models.Model):
    membership_default = 'B'
    MEMBERSHIP_CHOICES = {
        membership_default: 'Bronze',
        'S': 'Silver',
        'G': 'Gold',
    }
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=membership_default)


class Order(models.Model):
    payment_status_default = 'P'
    PAYMENT_STATUS = {
        payment_status_default: 'Pending',
        'C': 'Complete',
        'F': 'Failed',
    }
    
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS, default=payment_status_default
        )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT
    )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.PositiveIntegerField()


class Adress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE
        )

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
     

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    