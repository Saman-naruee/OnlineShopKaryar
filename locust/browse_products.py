from typing import override
from locust import HttpUser, between, task
from random import randint
from store.test_tools.tools import custom_logger

from urllib3 import response

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def view_products(self):
        custom_logger(f'Viewing products')
        collection_id = randint(1, 5)
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='/store/products'
        )
    
    @task
    def view_product_details(self):
        custom_logger(f'Viewing product details')
        product_id = randint(1, 1000)
        self.client.get(
            f'/store/products/{product_id}',
            name='/store/products/:id'
        )

    @task
    def add_to_cart(self):
        custom_logger("Adding to cart")
        product_id = randint(1, 10)
        self.client.post(
            f'/store/carts/{self.cart_id}/items/',
            name='/store/carts/items',
            json={'product_id': product_id, 'quantity': 1}
        )    

    @override
    def on_start(self) -> None:
        custom_logger("Starting")
        response = self.client.post('/store/carts/')
        result = response.json()
        self.cart_id = result['id']


