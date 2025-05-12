from rest_framework.test import APIClient
from rest_framework import status
import pytest
client = APIClient()

@pytest.mark.django_db
def test_if_user_is_anonymous_then_returns_401():
    # AAA (Arrange, Act, Assert)
    # Arrange

    # Act
    response = client.post("/store/collections/", {"title": "test"})
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"] == "Authentication credentials were not provided."


