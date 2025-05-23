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
        # create a cart
        self.cart = Cart.objects.create()
    
    def test_cart_creation(self):
        self.assertIsNotNone(self.cart.uid)

    def test_cart_string_representation(self):
        """Test the string representation of a cart"""
        expected_string = str(self.cart.uid)
        self.assertEqual(str(self.cart), expected_string)


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
            collection=self.collection
        )
        # create a review
        self.review = Review.objects.create(
            product=self.product,
            customer=self.customer,
            rating=5,
            comment='Test review comment'
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.customer, self.customer)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Test review comment')

    def test_review_string_representation(self):
        """Test the string representation of a review"""
        expected_string = f'{self.review.product.title} - {self.review.customer.user.username}'
        self.assertEqual(str(self.review), expected_string)
