from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Collection, Product, Customer, Notification

User = get_user_model()


class BaseModelTestCase(TestCase):
    """Base test case for model tests"""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com'
        )
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admintest@example.com'
        )
        
        # Create a customer
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            membership='B'  # Bronze membership
        )
        
        # Create a collection
        self.collection = Collection.objects.create(title='Test Collection')


class BaseAPITestCase(TestCase):
    """Base test case for API tests"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com'
        )
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admintest@example.com'
        )
        
        # Create a customer
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890',
            membership='B'  # Bronze membership
        )
        
        # Create a collection
        self.collection = Collection.objects.create(title='Test Collection')
    
    def authenticate_user(self, user=None):
        """Helper method to authenticate a user"""
        if user is None:
            user = self.user
        self.client.force_authenticate(user=user)
    
    def authenticate_admin(self):
        """Helper method to authenticate as admin"""
        self.client.force_authenticate(user=self.admin_user)
    
    def assign_permission(self, user, perm_codename):
        """Helper method to assign a permission to a user"""
        from django.contrib.auth.models import Permission
        permission = Permission.objects.get(codename=perm_codename)
        user.user_permissions.add(permission)
