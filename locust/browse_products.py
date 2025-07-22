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
            # If user was just created, we need to set the password properly
            user.set_password(data["password"])
            user.save()
            data.pop("password2")
            return data
        # If user already exists, return a dict with just username and password
        return {"username": data["username"], "password": data["password"]}
    
    @task(1)
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
    
    @task(2)
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


    @task(1)
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


class AuthenticationUser(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        self.username = "postgres"
        self.password = "postgres"
    
    @task
    def login(self):
        """Test user login performance"""
        custom_logger("Attempting login...")
        response = self.client.post(
            "/api/auth/login/",
            json={"username": self.username, "password": self.password},
            name="/api/auth/login"
        )
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result["access"]
            custom_logger(f"Login successful: {self.access_token[:15]}...")
        else:
            custom_logger(f"Login failed: {response.status_code} - {response.text}", color=Fore.RED)
    
    @task
    def refresh_token(self):
        """Test token refresh performance"""
        if not self.access_token:
            self.login()
            return
            
        # First login to get refresh token
        response = self.client.post(
            "/api/auth/login/",
            json={"username": self.username, "password": self.password}
        )
        
        if response.status_code == 200:
            refresh_token = response.json()["refresh"]
            
            # Then test refresh endpoint
            refresh_response = self.client.post(
                "/api/auth/refresh/",
                json={"refresh": refresh_token},
                name="/api/auth/refresh"
            )
            
            if refresh_response.status_code == 200:
                custom_logger("Token refresh successful")
            else:
                custom_logger(f"Token refresh failed: {refresh_response.status_code}", color=Fore.RED)
        else:
            custom_logger("Could not get refresh token", color=Fore.RED)


from locust import HttpUser, task, between
from random import randint, choice
from colorama import Fore
from store.test_tools.tools import custom_logger

class ProductBrowsingUser(HttpUser):
    wait_time = between(1, 5)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        self.collections = []
        self.product_ids = []
    
    def on_start(self):
        """Authenticate user and store the JWT token."""
        response = self.client.post(
            "/api/auth/login/",
            json={"username": "postgres", "password": "postgres"}
        )
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result["access"]
            custom_logger(f"Authentication successful: {self.access_token[:15]}...")
            
            # Get collections for later use
            self._get_collections()
            # Get some product IDs for later use
            self._get_product_ids()
        else:
            custom_logger(f"Authentication failed: {response.status_code}", color=Fore.RED)
    
    def get_auth_header(self):
        """Return authorization header with JWT token."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    def _get_collections(self):
        """Get available collections for testing."""
        response = self.client.get(
            "/store/collections/",
            headers=self.get_auth_header(),
            name="/store/collections"
        )
        
        if response.status_code == 200:
            collections = response.json()
            self.collections = [c["id"] for c in collections]
            custom_logger(f"Retrieved {len(self.collections)} collections")
        else:
            custom_logger("Failed to retrieve collections", color=Fore.RED)
    
    def _get_product_ids(self):
        """Get some product IDs for testing."""
        response = self.client.get(
            "/store/products/",
            headers=self.get_auth_header(),
            name="/store/products"
        )
        
        if response.status_code == 200:
            products = response.json()
            if isinstance(products, dict) and "results" in products:
                products = products["results"]  # Handle pagination
            
            self.product_ids = [p["id"] for p in products]
            custom_logger(f"Retrieved {len(self.product_ids)} product IDs")
        else:
            custom_logger("Failed to retrieve products", color=Fore.RED)
            # Fallback to some random IDs
            self.product_ids = list(range(1, 20))
    
    @task(3)
    def view_products(self):
        """Browse products with optional filtering."""
        params = {}
        
        # Randomly add collection filter
        if self.collections and randint(0, 1) == 1:
            collection_id = choice(self.collections)
            params["collection_id"] = collection_id
        
        # Randomly add search term
        if randint(0, 3) == 1:
            search_terms = ["product", "special", "new", "premium"]
            params["search"] = choice(search_terms)
        
        # Randomly add ordering
        if randint(0, 2) == 1:
            ordering_options = ["unit_price", "-unit_price", "last_update", "-last_update"]
            params["ordering"] = choice(ordering_options)
        
        response = self.client.get(
            "/store/products/",
            params=params,
            headers=self.get_auth_header(),
            name="/store/products"
        )
        
        if response.status_code == 200:
            custom_logger(f"Successfully viewed products with params: {params}")
        else:
            custom_logger(f"Failed to view products: {response.status_code}", color=Fore.RED)
    
    @task(2)
    def view_product_details(self):
        """View details of a specific product."""
        if not self.product_ids:
            custom_logger("No product IDs available for testing", color=Fore.YELLOW)
            return
        
        product_id = choice(self.product_ids)
        response = self.client.get(
            f"/store/products/{product_id}/",
            headers=self.get_auth_header(),
            name="/store/products/:id"
        )
        
        if response.status_code == 200:
            custom_logger(f"Successfully viewed product {product_id}")
        else:
            custom_logger(f"Failed to view product {product_id}: {response.status_code}", color=Fore.RED)
    
    @task(1)
    def view_product_reviews(self):
        """View reviews for a specific product."""
        if not self.product_ids:
            return
        
        product_id = choice(self.product_ids)
        response = self.client.get(
            f"/store/products/{product_id}/reveiws/",
            headers=self.get_auth_header(),
            name="/store/products/:id/reviews"
        )
        
        if response.status_code == 200:
            custom_logger(f"Successfully viewed reviews for product {product_id}")
        else:
            custom_logger(f"Failed to view reviews: {response.status_code}", color=Fore.RED)
