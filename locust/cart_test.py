from locust import HttpUser, task, between
from random import randint, choice
from colorama import Fore
import uuid
from store.test_tools.tools import custom_logger

class CartOperationsUser(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None
        self.cart_id = None
        self.product_ids = []
        self.cart_items = []
    
    def on_start(self):
        """Authenticate user and create a cart."""
        # Login
        response = self.client.post(
            "/api/auth/login/",
            json={"username": "postgres", "password": "postgres"}
        )
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result["access"]
            custom_logger(f"Authentication successful: {self.access_token[:15]}...")
            
            # Get product IDs
            self._get_product_ids()
            
            # Create a cart
            self._create_cart()
        else:
            custom_logger(f"Authentication failed: {response.status_code}", color=Fore.RED)
    
    def get_auth_header(self):
        """Return authorization header with JWT token."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    def _get_product_ids(self):
        """Get some product IDs for testing."""
        response = self.client.get(
            "/store/products/",
            headers=self.get_auth_header()
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
    
    def _create_cart(self):
        """Create a new cart."""
        response = self.client.post(
            "/store/carts/",
            headers=self.get_auth_header(),
            name="/store/carts"
        )
        
        if response.status_code == 201:
            result = response.json()
            self.cart_id = result["uid"]
            custom_logger(f"Created cart with ID: {self.cart_id}")
        else:
            custom_logger(f"Failed to create cart: {response.status_code} - {response.text}", color=Fore.RED)
    
    @task(3)
    def add_to_cart(self):
        """Add an item to the cart."""
        if not self.access_token or not self.cart_id or not self.product_ids:
            custom_logger("Missing required data for add_to_cart", color=Fore.YELLOW)
            return
        
        product_id = choice(self.product_ids)
        quantity = randint(1, 3)
        
        response = self.client.post(
            f"/store/carts/{self.cart_id}/items/",
            json={"product_id": product_id, "quantity": quantity},
            headers=self.get_auth_header(),
            name="/store/carts/:id/items"
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.cart_items.append(result["uid"] if "uid" in result else None)
            custom_logger(f"Added product {product_id} (qty: {quantity}) to cart")
        else:
            custom_logger(f"Failed to add to cart: {response.status_code} - {response.text}", color=Fore.RED)
    
    @task(2)
    def view_cart(self):
        """View the current cart."""
        if not self.access_token or not self.cart_id:
            return
        
        response = self.client.get(
            f"/store/carts/{self.cart_id}/",
            headers=self.get_auth_header(),
            name="/store/carts/:id"
        )
        
        if response.status_code == 200:
            custom_logger(f"Successfully viewed cart {self.cart_id}")
        else:
            custom_logger(f"Failed to view cart: {response.status_code}", color=Fore.RED)
    
    @task(1)
    def update_cart_item(self):
        """Update a cart item quantity."""
        if not self.access_token or not self.cart_id or not self.cart_items:
            return
        
        item_id = choice(self.cart_items)
        if not item_id:
            return
            
        new_quantity = randint(1, 5)
        
        response = self.client.patch(
            f"/store/carts/{self.cart_id}/items/{item_id}/",
            json={"quantity": new_quantity},
            headers=self.get_auth_header(),
            name="/store/carts/:id/items/:id"
        )
        
        if response.status_code == 200:
            custom_logger(f"Updated cart item quantity to {new_quantity}")
        else:
            custom_logger(f"Failed to update cart item: {response.status_code}", color=Fore.RED)
    
    @task(1)
    def remove_from_cart(self):
        """Remove an item from the cart."""
        if not self.access_token or not self.cart_id or not self.cart_items:
            return
        
        if not self.cart_items:
            return
            
        item_id = self.cart_items.pop()  # Remove and get the last item
        if not item_id:
            return
            
        response = self.client.delete(
            f"/store/carts/{self.cart_id}/items/{item_id}/",
            headers=self.get_auth_header(),
            name="/store/carts/:id/items/:id"
        )
        
        if response.status_code in [200, 204]:
            custom_logger(f"Removed item from cart")
        else:
            custom_logger(f"Failed to remove item: {response.status_code}", color=Fore.RED)
