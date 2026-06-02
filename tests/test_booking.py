import requests


BASE_URL = "https://restful-booker.herokuapp.com"


def test_full_booking_lifecycle(auth_token):
    # 1. Создание брони (POST /booking)
    create_url = f"{BASE_URL}/booking"
    payload = {
        "firstname": "Maksim",
        "lastname": "Kuznetcov",
        "totalprice": 200,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
        "additionalneeds": "Breakfast"
    }
    
    response = requests.post(create_url, json=payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]

    
    # 2. Полное обновление брони (PUT /booking/{id})
    update_url = f"{BASE_URL}/booking/{booking_id}"
    update_payload = {
        "firstname": "Andrey",
        "lastname": "Kuznetcov",
        "totalprice": 260,
        "depositpaid": False,
        "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
        "additionalneeds": "Extra pillows"
    }
    # Передаем токен авторизации через Cookie, как указано в документации
    headers = {"Cookie": f"token={auth_token}"}
    
    update_response = requests.put(update_url, json=update_payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["firstname"] == "Andrey"
    assert update_response.json()["depositpaid"] is False

    
    # 3. Удаление брони (DELETE /booking/{id})
    delete_response = requests.delete(update_url, headers=headers)
    assert delete_response.status_code == 201  # Специфика Restful-booker

    
    # 4. Проверка удаления (GET /booking/{id} -> Должно быть 404)
    get_response = requests.get(update_url)
    assert get_response.status_code == 404


def test_delete_booking_without_auth():
    # Негативный тест: Попытка удаления случайной брони без токена
    fake_booking_id = 999999
    url = f"{BASE_URL}/booking/{fake_booking_id}"
    
    # Отправляем запрос без заголовка Cookie
    response = requests.delete(url)
    assert response.status_code == 403  # Forbidden
