from datetime import date
from os import name
from typing import override
from django.db import IntegrityError
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from .models import Notification, Product, Collection, OrderItem, Review, Cart, \
    CartItem, Customer, Order, ProductImages, Promotion
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

    def tearDown(self):
        # Clean up test data
        User.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()


class ProductModelTest(TestCase):
    """Test the Product model"""
    
    def setUp(self):
        # create a collection
        self.collection = Collection.objects.create(title='Test Collection')
        
        # create a product
        self.product = Product.objects.create(
            title='Test Product',
            description='Test product description',
            unit_price=10.99,
            inventory=100,
            collection=self.collection
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.title, 'Test Product')
        self.assertEqual(self.product.description, 'Test product description')
        self.assertEqual(self.product.unit_price, 10.99)
        self.assertEqual(self.product.collection, self.collection)

    def test_product_string_representation(self):
        """Test the string representation of a product"""
        expected_string = self.product.title
        self.assertEqual(str(self.product), expected_string)

    def test_product_with_zero_inventory(self):
        product = Product.objects.create(
            title='Zero Inventory Product',
            description='Test',
            unit_price=10.99,
            inventory=0,
            collection=self.collection
        )
        self.assertEqual(product.inventory, 0)

    def test_product_negative_inventory(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                title='Invalid Product of Test',
                description='Test',
                unit_price=10.99,
                inventory=-1,
                collection=self.collection
            )


class CollectionModelTest(TestCase):
    """Test the Collection model"""
    
    def setUp(self):
        # create a collection
        self.collection = Collection.objects.create(title='Test Collection')
    
    def test_collection_creation(self):
        self.assertEqual(self.collection.title, 'Test Collection')

    def test_collection_string_representation(self):
        """Test the string representation of a collection"""
        expected_string = self.collection.title
        self.assertEqual(str(self.collection), expected_string)


class CartModelTest(TestCase):
    """Test the Cart model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            membership='B'
        )
        self.cart = Cart.objects.create(customer=self.customer)
    
    def test_cart_creation(self):
        self.assertIsNotNone(self.cart.uid)

    def test_cart_string_representation(self):
        """Test the string representation of a cart"""
        expected_string = str(self.cart.created_at)
        self.assertEqual(str(self.cart), expected_string)

    def test_cart_customer_permission(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_customer = Customer.objects.create(
            user=other_user,
            phone='9876543210',
            membership='B'
        )
        self.assertNotEqual(self.cart.customer, other_customer)


class ReviewModelTest(TestCase):
    """Test the Review model"""
    
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
        # create a collection
        self.collection = Collection.objects.create(title='Test Collection')
        # create a product
        self.product = Product.objects.create(
            title='Test Product',
            description='Test product description',
            unit_price=10.99,
            inventory=100,
            collection=self.collection
        )
        # create a review
        self.review = Review.objects.create(
            product=self.product,
            name='Test Review',
            description='Test review description',
            user=self.customer
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.name, 'Test Review')
        self.assertEqual(self.review.description, 'Test review description')


class CustomerModelTest(TestCase):
    """Test the Customer model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            membership='B'
        )
    
    def test_customer_creation(self):
        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.phone, '1234567890')
        self.assertEqual(self.customer.membership, 'B')
