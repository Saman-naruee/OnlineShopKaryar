from django.db import models

class Collection(models.Model):
    title = models.CharField(max_length=255)

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12)
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, 
        )


class Customer(models.Model):
    membership_default = 'B'
    MEMBERSHIP_CHOICES = [
        (membership_default, 'Bronze'),
        ('S', 'Silver'),
        ('G', 'Gold'),
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=membership_default)


class Order(models.Model):
    payment_status_default = 'P'
    PAYMENT_STATUS = [
        ('P', 'Pending')
        ('C', 'Complete')
        ('F', 'Failed')
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS, default=payment_status_default
        )


class Adress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE
        )
