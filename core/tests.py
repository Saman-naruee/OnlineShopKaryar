from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class UserAuthenticationTest(TestCase):
    """Test class for user registration and authentication"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/users/profile/'
        
        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Create an existing user for duplicate tests
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123',
            first_name='Existing',
            last_name='User'
        )

    # Registration Tests
    def test_user_registration_success(self):
        """Test successful user registration with valid data"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_registration_missing_fields(self):
        """Test registration fails when required fields are missing"""
        required_fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        
        for field in required_fields:
            data = self.user_data.copy()
            data.pop(field)
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        data = self.user_data.copy()
        data['username'] = 'existinguser'
        data['email'] = 'new@example.com'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_email(self):
        """Test registration fails with invalid email format"""
        invalid_emails = ['invalid-email', 'test@', '@example.com', 'test@.com']
        
        for email in invalid_emails:
            data = self.user_data.copy()
            data['email'] = email
            response = self.client.post(self.register_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('email', response.data)

    def test_user_registration_password_validation(self):
        """Test password validation during registration"""
        # Test password mismatch
        data = self.user_data.copy()
        data['password2'] = 'differentpass123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

        # Test short password
        data = self.user_data.copy()
        data['password'] = data['password2'] = 'short'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test numeric-only password
        data = self.user_data.copy()
        data['password'] = data['password2'] = '12345678'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test common password
        data = self.user_data.copy()
        data['password'] = data['password2'] = 'password123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test password similar to username
        data = self.user_data.copy()
        data['password'] = data['password2'] = f'{data["username"]}123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Login Tests
    def test_user_login_success(self):
        """Test successful login with valid credentials"""
        # First register a user
        self.client.post(self.register_url, self.user_data)
        
        # Try to login
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        # Test with wrong password
        response = self.client.post(self.login_url, {
            'username': self.existing_user.username,
            'password': 'wrongpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test with non-existent user
        response = self.client.post(self.login_url, {
            'username': 'nonexistentuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Profile Tests
    def test_get_profile_authenticated(self):
        """Test retrieving profile when authenticated"""
        # First register and login
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        token = response.data['access']
        
        # Get profile with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['first_name'], self.user_data['first_name'])
        self.assertEqual(response.data['last_name'], self.user_data['last_name'])

    def test_get_profile_unauthenticated(self):
        """Test retrieving profile fails when unauthenticated"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_success(self):
        """Test successful profile update"""
        # First register and login
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Update profile
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')

        # Verify changes in database
        user = User.objects.get(username=self.user_data['username'])
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')

    def test_update_profile_email_protected(self):
        """Test that email cannot be changed after registration"""
        # First register and login
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Try to update email
        update_data = {
            'email': 'newemail@example.com'
        }
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

        # Verify email hasn't changed
        user = User.objects.get(username=self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])

    def test_token_refresh(self): 
        """Test refreshing access token"""
        # First register and login
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        refresh_token = response.data['refresh']
        
        # Try to refresh token
        refresh_url = '/api/auth/refresh/'
        response = self.client.post(refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_token_refresh(self):
        """Test refreshing token fails with invalid refresh token"""
        refresh_url = '/api/auth/refresh/'
        response = self.client.post(refresh_url, {'refresh': 'invalid-token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
