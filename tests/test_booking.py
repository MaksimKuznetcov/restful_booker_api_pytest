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
    def test_health_check(self):
        """Проверка доступности API (Ping)"""
        
        url = f"{BASE_URL}/Ping"
        
        with allure.step("Отправка GET-запроса на эндпоинт /ping"):
            response = requests.get(url)
            allure.attach(f"Статус: {response.status_code}", name="Результат Ping")
            assert response.status_code == 201
        

    # Позитивные тесты booking:

    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Успешное создание бронирования")
    @pytest.mark.run(order=2)
    def test_create_booking(self):
        """Создание брони (POST)"""
        
        global BOOKING_ID
        url = f"{BASE_URL}/booking"
        payload = {
            "firstname": "Maksim",
            "lastname": "Kuznetcov",
            "totalprice": 200,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
            "additionalneeds": "Breakfast"
        }

        with allure.step("Отправка POST-запроса на создание брони"):
            response = requests.post(url, json=payload)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки POST-запроса")
            assert response.status_code == 200
        
        with allure.step("Логирование JSON запроса и ответа"):
            allure.attach(json.dumps(payload, indent=4), name="Отправленный JSON-Body (POST)", attachment_type=allure.attachment_type.JSON)
            allure.attach(json.dumps(response.json(), indent=4), name="Ответ бэкенда (JSON)", attachment_type=allure.attachment_type.JSON)

        # Сохранение ID
        BOOKING_ID = response.json()["bookingid"]
        assert BOOKING_ID is not None


    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Получение конкретного бронирования по ID")
    @pytest.mark.run(order=3)
    def test_get_booking(self):
        """Проверка получения данных о брони по id"""
        
        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")
        
        url = f"{BASE_URL}/booking/{BOOKING_ID}"

        with allure.step(f"Отправка GET-запроса для получения брони по ID: {BOOKING_ID}"):
            response = requests.get(url)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки GET-запроса")
            assert response.status_code == 200
        
        with allure.step("Проверка соответствия данных"):
            assert response.json()["firstname"] == "Maksim"
            assert response.json()["lastname"] == "Kuznetcov"


    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Получение полного списка ID бронирований")
    @pytest.mark.run(order=4)
    def test_get_booking_ids(self):
        """Проверка получения списка id броней"""
        
        url = f"{BASE_URL}/booking"

        with allure.step("Отправка GET-запроса на получение всех ID бронирований"):
            response = requests.get(url)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки GET-запроса")
            assert response.status_code == 200


    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Получение списка бронирований по фильтрам")
    @pytest.mark.run(order=5)
    def test_get_booking_ids_query_parameters(self):
        "Проверка фильтрации бронирований через параметры запроса (Query Parameters)"
        
        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")

        url = f"{BASE_URL}/booking"
        parameters = {
            "firstname": "Maksim",
            "lastname": "Kuznetcov"
        }

        with allure.step("Отправка GET-запроса с фильтрами по имени"):
            response = requests.get(url, params=parameters)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки GET-запроса")
            assert response.status_code == 200
        
        with allure.step("Логирование параметров и ответа"):
            allure.attach(json.dumps(parameters, indent=4), name="Query-параметры запроса", attachment_type=allure.attachment_type.JSON)
            allure.attach(json.dumps(response.json(), indent=4), name="Ответ бэкенда (JSON)", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Валидация структуры ответа и типов данных"):
            # Проверяем что ответ на запрос является массивом
            booking_list = response.json()
            assert isinstance(booking_list, list)

            # Проверяем что массив не пустой
            assert len(booking_list) > 0
            
            # Проверяем наличие ключа bookingid и то что его значение число
            for booking in booking_list:
                assert "bookingid" in booking
                assert isinstance(booking["bookingid"], int)


    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Полное обновление данных бронирования")
    @pytest.mark.run(order=6)
    def test_update_booking(self, auth_token):
        """Полное обновление брони (PUT)"""
        
        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")
        
        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        headers = {"Cookie": f"token={auth_token}"}
        payload = {
            "firstname": "Andrey",
            "lastname": "Kuznetcov",
            "totalprice": 260,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
            "additionalneeds": "Extra pillows"
        }
        
        with allure.step("Отправка PUT-запроса на обновление брони"):
            response = requests.put(url, json=payload, headers=headers)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки PUT-запроса")
            assert response.status_code == 200
        
        with allure.step("Логирование JSON запроса и ответа"):
            allure.attach(json.dumps(payload, indent=4), name="Отправленный JSON-Body (PUT)", attachment_type=allure.attachment_type.JSON)
            allure.attach(json.dumps(response.json(), indent=4), name="Ответ бэкенда (JSON)", attachment_type=allure.attachment_type.JSON)
                                        
        with allure.step("Проверка измененных данных"):
            assert response.json()["firstname"] == "Andrey"
            assert response.json()["depositpaid"] is False


    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Частичное обновление данных бронирования")
    @pytest.mark.run(order=7)
    def test_partial_update_booking(self, auth_token):
        """Частичное обновление брони (PATCH)"""

        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")

        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        headers = {"Cookie": f"token={auth_token}"}
        payload = {
            "totalprice": 350,
            "depositpaid": True
        }
        
        with allure.step("Отправка PATCH-запроса на частичное изменение имени"):
            response = requests.patch(url, json=payload, headers=headers)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки PATCH-запроса")
            assert response.status_code == 200
        
        with allure.step("Логирование JSON запроса и ответа"):
            allure.attach(json.dumps(payload, indent=4), name="Отправленный JSON-Body (PATCH)", attachment_type=allure.attachment_type.JSON)
            allure.attach(json.dumps(response.json(), indent=4), name="Ответ бэкенда (JSON)", attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Проверка что данные действительно обновились"):
            assert response.json()["totalprice"] == 350
            assert response.json()["depositpaid"] is True
        
        with allure.step("Проверка что остальные поля сохранили корректные типы данных"):
            assert isinstance(response.json()["firstname"], str)
            assert isinstance(response.json()["lastname"], str)
            assert isinstance(response.json()["totalprice"], (int, float))
            assert isinstance(response.json()["depositpaid"], bool)
            assert isinstance(response.json()["additionalneeds"], str)
        
        with allure.step("Проверка вложенного объекта bookingdates"):
            booking_dates = response.json().get("bookingdates")
            assert isinstance(booking_dates, dict)
            assert isinstance(booking_dates.get("checkin"), str)
            assert isinstance(booking_dates.get("checkout"), str)


    @allure.feature("Управление бронированиями (CRUD)")
    @allure.story("Удаление бронирования")
    @pytest.mark.run(order=8)
    def test_delete_booking(self, auth_token):
        """Удаление созданной брони (DELETE)"""

        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")

        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        headers = {"Cookie": f"token={auth_token}"}

        with allure.step("Отправка DELETE-запроса на удаление брони"):
            response = requests.delete(url, headers=headers)
            allure.attach(f"Статус: {response.status_code}", name="Результат удаления")
            assert response.status_code == 201  # Специфика Restful-booker

        with allure.step("Проверка удаления брони (запрос должен вернуть 404)"):
            get_response = requests.get(url)
            allure.attach(f"Статус: {get_response.status_code}", name="Результат повторного GET запроса")
            assert get_response.status_code == 404


    # Негативные тесты booking:

    @allure.feature("Безопасность и авторизация")
    @allure.story("Отклонение запроса на обновление без токена")
    @pytest.mark.run(order=9)
    def test_update_booking_without_auth(self):
        """Проверка полного обновления данных брони (без токена авторизации)"""
        
        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")

        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        payload = {
            "firstname": "Andrey",
            "lastname": "Kuznetcov",
            "totalprice": 260,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-15"},
            "additionalneeds": "Extra pillows"
        }

        with allure.step("Отправка PUT-запроса БЕЗ заголовка Cookie с токеном"):
            response = requests.put(url, json=payload)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки PUT-запроса (ожидается 403)")
            assert response.status_code == 403


    @allure.feature("Безопасность и авторизация")
    @allure.story("Отклонение запроса на удаление без токена")
    @pytest.mark.run(order=10)
    def test_delete_booking_without_auth(self):
        """Проверка удаления брони (без токена авторизиции)"""

        if BOOKING_ID is None:
            pytest.fail("Тест пропущен: Бронь не была создана на предыдущем шаге")

        url = f"{BASE_URL}/booking/{BOOKING_ID}"
        
        with allure.step("Отправка DELETE-запроса БЕЗ заголовка Cookie с токеном"):
            response = requests.delete(url)
            allure.attach(f"Статус: {response.status_code}", name="Результат отправки DELETE-запроса (ожидается 403)")
            assert response.status_code == 403


    @allure.feature("Валидация бизнес-логики")
    @allure.story("Отклонение бронирования со сквозными датами (checkout раньше checkin)")
    @pytest.mark.run(order=11)
    def test_create_booking_incorrect_dates(self):
        """Проверка создание брони с некорректными датами (Логика дат)"""
        
        url = f"{BASE_URL}/booking"
        payload = {
            "firstname": "Maksim",
            "lastname": "Kuznetcov",
            "totalprice": 200,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-12-31", "checkout": "2026-01-01"},
            "additionalneeds": "Breakfast"
        }

        with allure.step("Отправка POST-запроса с перевернутыми датами"):
            response = requests.post(url, json=payload)

        with allure.step("Логирование запроса и ответа бэкенда"):
            allure.attach(json.dumps(payload, indent=4), name="Отправленный невалидный JSON (Даты)", attachment_type=allure.attachment_type.JSON)
            try:
                allure.attach(json.dumps(response.json(), indent=4), name="Ответ бэкенда (JSON)", attachment_type=allure.attachment_type.JSON)
            except Exception:
                allure.attach(f"Статус-код: {response.status_code}\nТело ответа:\n{response.text}", name="Ответ бэкенда (Текст/Строка)")

        # Ловушка для бага: если сервер вернул 200
        if response.status_code == 200:
            pytest.fail(f"КРИТИЧЕСКИЙ БАГ: Бэкенд успешно создал бронь с некорректными датами! Ответ бэкенда: {response.json()}")
        
        # Ловушка для падения сервера (на случай, если он упадет в 500)
        if response.status_code == 500:
            pytest.fail("КРИТИЧЕСКИЙ СБОЙ: Сервер упал с ошибкой 500 Internal Server Error")

        # Ожидаемое эталонное поведение по документации (тест пройдет успешно, если вернется 400)
        assert response.status_code == 400


    @allure.feature("Валидация полей бэкенда")
    @allure.story("Автоматическое полейное негативное тестирование (DDT)")
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
    def test_booking_invalid_payload_ddt(self, valid_booking_payload, field_path, invalid_value, case_name):
        """Параметризованный тест-ловушка для отлова багов валидации полей."""
        
        url = f"{BASE_URL}/booking"
        payload = valid_booking_payload.copy()  # Чистая копия фикстуры
        
        # Логика порчи данных: если поле вложенное (содержит точку), или обычное
        if "." in field_path:
            parent, child = field_path.split(".")
            payload[parent] = payload[parent].copy() # защищаем фикстуру от перезаписи
            payload[parent][child] = invalid_value
        else:
            payload[field_path] = invalid_value
            
        with allure.step(f"Запуск негативного кейса: {case_name}"):
            response = requests.post(url, json=payload)
        
        with allure.step("Логирование запроса и ответа бэкенда"):
            allure.attach(json.dumps(payload, indent=4, ensure_ascii=False), name="Отправленный невалидный JSON", attachment_type=allure.attachment_type.JSON)
            try:
                # Пытаемся прикрепить красивый JSON ответа, если сервер его прислал
                allure.attach(json.dumps(response.json(), indent=4, ensure_ascii=False), name="Ответ сервера (JSON)", attachment_type=allure.attachment_type.JSON)
            except Exception:
                # Если сервер упал в 500 и прислал обычный текст вместо JSON
                allure.attach(f"Статус-код: {response.status_code}\nТело ответа:\n{response.text}", name="Ответ сервера (Текст/Строка)")

        # Ловушка для бага: если сервер вернул 200
        if response.status_code == 200:
            pytest.fail(f"КРИТИЧЕСКИЙ БАГ: Сервер сохранил невалидные данные и вернул 200 OK в кейсе: '{case_name}'")

        # Ловушка для падения сервера (на случай, если он упадет в 500)
        if response.status_code == 500:
            pytest.fail(f"КРИТИЧЕСКИЙ БАГ: Сервер упал в 500 ошибку на кейсе: '{case_name}'")
            
        # Ожидаемое эталонное поведение по документации (тест пройдет успешно, если вернется 400)
        assert response.status_code == 400