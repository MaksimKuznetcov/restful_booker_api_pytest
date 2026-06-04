import allure
import json
import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"
BOOKING_ID = None   # Глобальная переменная для передачи ID созданной брони между тестами


@allure.epic("Тестирование REST API сервиса Restful-Booker")
class TestBookingLifecycle:

    @allure.feature("Доступность сервиса (Health Check)")
    @allure.story("Проверка работоспособности API")
    @pytest.mark.run(order=1)
    def test_health_check():
        """Проверка доступности API (Ping)"""
        url = f"{BASE_URL}/Ping"
        
        with allure.step("Отправка GET-запроса на эндпоинт /ping"):
            response = requests.get(url)
        
        with allure.step("Логирование ответа"):
            allure.attach(f"Статус: {response.status_code}\nОтвет: {response.text}", name="Результат Ping")

        with allure.step("Проверка, что сервер вернул статус 201 Created"):
            assert response.status_code == 201


    # Позитивные тесты booking:


    def test_create_booking():
        """Проверка создание брони"""
        url = f"{BASE_URL}/booking"
        payload = {
            "firstname": "Maksim",
            "lastname": "Kuznetcov",
            "totalprice": 200,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
            "additionalneeds": "Breakfast"
        }
        global BOOKING_ID

        response = requests.post(url, json=payload)
        assert response.status_code == 200

        BOOKING_ID = response.json()["bookingid"]
        assert BOOKING_ID is not None


    def test_get_booking():
        """Проверка получения данных о брони по id"""
        url = f"{BASE_URL}/booking/{BOOKING_ID}"

        response = requests.get(url)
        assert response.status_code == 200
        assert response.json()["firstname"] == "Maksim"
        assert response.json()["lastname"] == "Kuznetcov"


    def test_get_booking_ids():
        """Проверка получения списка id броней"""
        url = f"{BASE_URL}/booking"

        response = requests.get(url)
        assert response.status_code == 200


    def test_get_booking_ids_query_parameters():
        "Проверка получения списка id броней при определенных параметрах"
        url = f"{BASE_URL}/booking"
        parameters = {
            "firstname": "Maksim",
            "lastname": "Kuznetcov"
        }

        response = requests.get(url, params=parameters)
        assert response.status_code == 200

        # Проверяем что ответ на запрос является массивом
        booking_list = response.json()
        assert isinstance(booking_list, list)

        # Проверяем что массив не пустой
        assert len(booking_list) > 0
        
        # Проверяем наличие ключа bookingid и то что его значение число
        for booking in booking_list:
            assert "bookingid" in booking
            assert isinstance(booking["bookingid"], int)


    def test_update_booking(auth_token):
        """Проверка полного обновления данных брони по id (с токеном авторизиции)"""
        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        payload = {
            "firstname": "Andrey",
            "lastname": "Kuznetcov",
            "totalprice": 260,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
            "additionalneeds": "Extra pillows"
        }
        # Передаем токен авторизации через Cookie, как указано в документации
        headers = {"Cookie": f"token={auth_token}"}

        response = requests.put(url, json=payload, headers=headers)
        assert response.status_code == 200
        
        # Проверяем что значения действительно обновились
        assert response.json()["firstname"] == "Andrey"
        assert response.json()["depositpaid"] is False


    def test_partial_update_booking(auth_token):
        """Проверка частичного обновления данных брони по id (с токеном авторизиции)"""
        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        payload = {
            "totalprice": 350,
            "depositpaid": True
        }
        headers = {"Cookie": f"token={auth_token}"}

        response = requests.patch(url, json=payload, headers=headers)
        assert response.status_code == 200
        
        # Проверяем что значения действительно обновились
        assert response.json()["totalprice"] == 350
        assert response.json()["depositpaid"] is True
        
        # Проверяем что остальные поля сохранили корректные типы данных
        assert isinstance(response.json()["firstname"], str)
        assert isinstance(response.json()["lastname"], str)
        assert isinstance(response.json()["totalprice"], (int, float))
        assert isinstance(response.json()["depositpaid"], bool)
        assert isinstance(response.json()["additionalneeds"], str)
        
        # Проверяем вложенный объект bookingdates
        booking_dates = response.json().get("bookingdates")
        assert isinstance(booking_dates, dict)
        assert isinstance(booking_dates.get("checkin"), str)
        assert isinstance(booking_dates.get("checkout"), str)


    def test_delete_booking(auth_token):
        """Проверка удаления брони (с токеном авторизиции)"""
        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        headers = {"Cookie": f"token={auth_token}"}

        response = requests.delete(url, headers=headers)
        assert response.status_code == 201  # Специфика Restful-booker

        # Проверка удаления (код GET запроса должен быть 404)
        get_response = requests.get(url)
        assert get_response.status_code == 404


    # Негативные тесты booking:


    def test_update_booking_without_auth():
        """Проверка полного обновления данных брони по id (без токена авторизиции)"""
        url = f"{BASE_URL}/booking/1"
        payload = {
            "firstname": "Andrey",
            "lastname": "Kuznetcov",
            "totalprice": 260,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
            "additionalneeds": "Extra pillows"
        }

        response = requests.put(url, json=payload)
        assert response.status_code == 403


    def test_delete_booking_without_auth():
        """Проверка удаления брони (без токена авторизиции)"""
        url = f"{BASE_URL}/booking/1"
        
        response = requests.delete(url)
        assert response.status_code == 403


    def test_create_booking_incorrect_dates():
        """Проверка создание брони с некорректными датами"""
        url = f"{BASE_URL}/booking"
        payload = {
            "firstname": "Maksim",
            "lastname": "Kuznetcov",
            "totalprice": 200,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-12-31", "checkout": "2026-01-01"},
            "additionalneeds": "Breakfast"
        }

        response = requests.post(url, json=payload)

        # Ловушка для бага: если сервер вернул 200
        if response.status_code == 200:
            pytest.fail(f"КРИТИЧЕСКИЙ БАГ: Бэкенд успешно создал бронь с некорректными датами! Ответ бэкенда: {response.json()}")
        
        # Ловушка для падения сервера (на случай, если он упадет в 500)
        if response.status_code == 500:
            pytest.fail("КРИТИЧЕСКИЙ СБОЙ: Сервер упал с ошибкой 500 Internal Server Error")

        # Ожидаемое эталонное поведение по документации (тест пройдет успешно, если вернется 400)
        assert response.status_code == 400


    @pytest.mark.parametrize(
        "field_path, invalid_value, case_name",
        [
            ("firstname", 12345, "Имя в виде числа"),
            ("firstname", None, "Имя со значением null"),
            ("totalprice", -500, "Отрицательная цена"),
            ("totalprice", "two hundred", "Цена строкой"),
            ("depositpaid", "yes", "Депозит строкой 'yes'"),
            ("bookingdates.checkin", "not-a-date", "Некорректный формат даты заезда"),
        ],
        ids=[
            "firstname_int", "firstname_null", "price_string", 
            "price_negative", "deposit_string", "date_format"
        ]
    )
    def test_booking_invalid_payload_ddt(valid_booking_payload, field_path, invalid_value, case_name):
        """Проверка создания брони с подстановкой невалидных данных (Data-Driven тест)"""
        url = f"{BASE_URL}/booking"
        # Чистая копия фикстуры
        payload = valid_booking_payload.copy()
        
        # Логика порчи данных: если поле вложенное (содержит точку), или обычное
        if "." in field_path:
            parent, child = field_path.split(".")
            payload[parent] = payload[parent].copy() # защищаем фикстуру от перезаписи
            payload[parent][child] = invalid_value
        else:
            payload[field_path] = invalid_value
            
        # Отправляем испорченный JSON на бэкенд
        response = requests.post(url, json=payload)
        
        # Ловушка для бага: если сервер вернул 200
        if response.status_code == 200:
            pytest.fail(f"КРИТИЧЕСКИЙ БАГ: Сервер сохранил невалидные данные и вернул 200 OK в кейсе: '{case_name}'")

        # Ловушка для падения сервера (на случай, если он упадет в 500)
        if response.status_code == 500:
            pytest.fail(f"КРИТИЧЕСКИЙ БАГ: Сервер упал в 500 ошибку на кейсе: '{case_name}'")
            
        # Ожидаемое эталонное поведение по документации (тест пройдет успешно, если вернется 400)
        assert response.status_code == 400