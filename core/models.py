from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # Note: Password validation is handled by Django's AUTH_PASSWORD_VALIDATORS setting
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
