import factory
from factory import Faker
from .models import Customer
import random

class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    email = Faker('email')
    phone = factory.LazyAttribute(lambda _: f"+98-{random.randint(915, 991)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}")
    birth_date = Faker('date_of_birth', minimum_age=18, maximum_age=90)

    membership = factory.LazyAttribute(lambda _: random.choice([
        Customer.MEMBERSHIP_BRONZE,
        Customer.MEMBERSHIP_SILVER,
        Customer.MEMBERSHIP_GOLD
    ]))
