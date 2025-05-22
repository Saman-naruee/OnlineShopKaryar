from typing import override
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from .models import Notification, Product, Collection, OrderItem, Review, Cart, \
    CartItem, Customer, Order, ProductImages
from .serializer import ProductSerializer,\
    CollectionSerializer, ReviewSerializer, CartSerializer,\
    CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer,\
    UserProfileSerializer, OrderListSerializer, UserNotificationsSerializer, \
    CreateOrderSerializer, UpdateOrderSerializer, ProductImageSerializer
import json

User = get_user_model()


class NotificationModelTest(TestCase):
    """Test the Notification model"""
    
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com'
        )
        # create a customer
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            membership='B' # Bronze membership
        )

        # create a notification
        self.notification = Notification.objects.create(
            user=self.customer,
            message='Test notification',
            is_admin=False,
            status='U' # Unread
        )
    
    def test_notification_creation(self):
        self.assertEqual(self.notification.message, 'Test notification')
        self.assertEqual(self.notification.is_admin, False)
        self.assertEqual(self.notification.status, 'U')
        self.assertEqual(self.notification.user, self.customer)

    def test_notification_string_representation(self):
        """Test the string representation of a notification"""
        expected_string = f'{self.notification.message} - {self.notification.user.user.username}'
        self.assertEqual(str(self.notification), expected_string)

