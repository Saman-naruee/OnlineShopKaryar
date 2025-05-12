from rest_framework.test import APIClient
from rest_framework import status

client = APIClient()


def test_if_user_is_anonymous_then_returns_401(client):
    # AAA (Arrange, Act, Assert)
    # Arrange

    # Act
    response = client.post("/store/collections/", {"name": "test"})
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == "Authentication credentials were not provided."


