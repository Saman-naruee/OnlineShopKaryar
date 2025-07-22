from locust import HttpUser, task, between
from random import randint, choice
from colorama import Fore
from store.test_tools.tools import custom_logger

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
