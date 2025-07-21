import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')

# Initialize Django
django.setup()


from typing import override
from locust import HttpUser, between, task
from random import randint
from store.test_tools.tools import custom_logger
from colorama import Fore, Style
from urllib3 import response
from core.models import User

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None


    @override
    def on_start(self) -> None:
        """
        Authenticate user and store the JWT token.
        """
        user = self.get_user_data()
        if user:
            password = user['password']
            username = user['username']

        try:
            response = self.client.post(
                "/api/auth/login/",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            result = response.json()
            self.access_token = result["access"]
            custom_logger(f"Authentication successful: {self.access_token[:15]}... .")

            # Create a cart after successful authentication
            response = self.client.post('/store/carts/', headers=self.get_auth_header())
            response.raise_for_status()
            result = response.json()
            self.cart_id = result['uid']
            custom_logger(f"Cart created with ID: {self.cart_id}")
        except Exception as e:
            custom_logger(f"Authentication or cart creation failed: ##\n{str(e)}\n##", color=Fore.RED)
            self.access_token = None  # Ensure token is None on failure
            self.cart_id = None
            return
        
    

    def get_auth_header(self):
        """
        Return authorization header with JWT token.
        """
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    
    def get_user_data(self):
        data = {
        "username": "mytresalsdkfuser",
        "email": "mytresalsdkfuser@gmail.com",
        "password": "testjoahn123@",
        "password2": "testjoahn123@",
        "first_name": "Test",
        "last_name": "User"
        }
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={key: value for key, value in data.items() if key != "password2"}
        )
        if created:
            data.pop("password2")
            return data
        return user.__dict__
    
    @task
    def view_products(self):
        """
        View products with authentication.
        """
        if not self.access_token:
            custom_logger("Skipping view_products task: No access token available.")
            return

        custom_logger("Viewing products...")
        collection_id = randint(1, 5)
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='/store/products',
            headers=self.get_auth_header()
        )
    
    @task
    def view_product_details(self):
        """
        View product details with authentication.
        """
        if not self.access_token:
            custom_logger("Skipping view_product_details: No access token")
            return

        product_id = randint(1, 1000)
        self.client.get(
            f'/store/products/{product_id}',
            name='/store/products/:id',
            headers=self.get_auth_header()  # Add auth header
        )


    @task
    def add_to_cart(self):
        """
        Add to cart with authentication.
        """
        if not self.access_token or not self.cart_id:
            custom_logger("Skipping add_to_cart: No access token or cart ID")
            return

        product_id = randint(1, 10)
        # Fix the URL format - it should include the cart_id in the path
        custom_logger(f"Cart ID: {self.cart_id}")

        response = self.client.post(
            f'/store/carts/{self.cart_id}/items/',
            name='/store/carts/items',
            json={'product_id': product_id, 'quantity': 1},
            headers=self.get_auth_header()
        )
        
        if response.status_code == 200 or response.status_code == 201:
            custom_logger(f"Successfully added product {product_id} to cart {self.cart_id}")
        else:
            custom_logger(f"Failed to add product to cart: {response.status_code} - {response.text}", color=Fore.RED)
        custom_logger(f"Response Status Code: {response.status_code}")
