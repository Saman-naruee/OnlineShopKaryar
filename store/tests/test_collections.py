from rest_framework.test import APIClient
from rest_framework import status

client = APIClient()


def test_if_user_is_anonymous_then_returns_403(client):
    # AAA (Arrange, Act, Assert)
    # Arrange

    # Act
    respones = client.post("/store/collections/", {"name": "test"})
    # Assert
    assert respones.status_code == status.HTTP_403_FORBIDDEN
    assert respones.data["detail"] == "Authentication credentials were not provided."
    

