# Автоматизация тестирования API Restful-Booker

Проект содержит набор ручных и автоматических тестов для учебного API бронирования отелей Restful-Booker.

## Стек технологий
* **Ручное тестирование**: Postman
* **Автоматизация**: Python 3, Pytest, Requests
* **CI/CD**: GitHub Actions (в процессе настройки)

## Структура проекта
* `Restful_Booker_Postman_Collection.json` — экспортированная коллекция ручных тестов Postman с настроенными скриптами автоматической передачи токенов.
* `tests/conftest.py` — конфигурация Pytest и фикстура автоматической авторизации (`auth_token`).
* `tests/test_booking.py` — позитивные автотесты сквозного сценария (CRUD) и негативные проверки безопасности.

## Как запустить автотесты локально
1. Установите зависимости: `pip install -r requirements.txt`
2. Запустите тесты: `pytest`

## О проекте
В качестве объекта тестирования используется популярный учебный сервис бронирования отелей **Restful-Booker**.

* **Сайт проекта / Тестовый стенд:** [**Restful-Booker**](https://restful-booker.herokuapp.com/)
* **Официальная API Документация:** [**Restful-Booker: API Docs**](https://herokuapp.comapidoc/index.html)
* **Код:** [**Restful-Booker: Github**](https://github.com/mwinteringham/restful-booker)
