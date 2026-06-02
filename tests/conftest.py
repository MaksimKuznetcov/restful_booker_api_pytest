import pytest
import requests

@pytest.fixture(scope="session")
def auth_token():
    """Фикстура для генерации токена авторизации (Auth - CreateToken)"""
    url = "https://restful-booker.herokuapp.com/auth"
    payload = {
        "username": "admin",
        "password": "password123"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    return response.json()["token"]
