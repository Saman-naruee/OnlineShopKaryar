from locust import HttpUser, task, between
from random import randint, choice
from colorama import Fore
from store.test_tools.tools import custom_logger


class ProductBrowsingUser(HttpUser):
    host = "http://127.0.0.1:8000"
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
            json={"username": "postgres", "password": "UIui!@#123"}
        )
        custom_logger(f"response.status_code: {response.status_code}", Fore.GREEN)
        
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
    
    @task(1)
    def say_hello(self):
        self.client.get("/playground/task/")
