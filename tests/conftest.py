import pytest
import requests


@pytest.fixture(scope="session")    # Для уровня session код фикстуры запускается ровно 1 раз за весь цикл тестов.
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


@pytest.fixture
def valid_booking_payload():
    """Возвращает валидный, эталонный набор данных для создания бронирования."""
    return {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
        "additionalneeds": "Breakfast"
    }