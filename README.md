<a name="ru"></a>

# Toj Market

Toj Market - это полнофункциональная платформа для электронной коммерции, созданная с использованием Django и Django REST Framework. Она предоставляет REST API для управления пользователями, товарами, магазинами и заказами. Проект также включает в себя Telegram-бота для продавцов, который позволяет им управлять своими магазинами на ходу.

## Содержание

- [Toj Market](#toj-market)
  - [Содержание](#содержание)
  - [Особенности](#особенности)
  - [Используемые технологии](#используемые-технологии)
  - [Настройка и установка](#настройка-и-установка)
  - [Запуск приложения](#запуск-приложения)
  - [Запуск Telegram-бота](#запуск-telegram-бота)
  - [Структура проекта](#структура-проекта)
- [Toj Market (English)](#en)

---

## Особенности

- **Аутентификация и управление пользователями:** JWT-аутентификация (access и refresh токены), регистрация, вход, профиль пользователя.
- **Роли пользователей:** Администратор, Покупатель, Продавец.
- **Магазины:** Продавцы могут создавать и управлять своими магазинами.
- **Товары:** CRUD-операции для товаров с изображениями, категориями, скидками и отзывами.
- **Корзина и Заказы:** Полноценная система корзины и заказов.
- **Поиск:** История поиска.
- **REST API:** Полноценный REST API с документацией Swagger (OpenAPI).
- **Telegram-бот для продавцов:**
  - Просмотр и управление заказами.
  - Просмотр и удаление товаров.
  - Просмотр статистики магазина.
  - Связывание Telegram-аккаунта с аккаунтом на сайте.

## Используемые технологии

- **Бэкенд:**
  - Python 3
  - Django
  - Django REST Framework
  - Django Simple JWT
  - drf-yasg (Swagger)
- **База данных:**
  - SQLite3 (для разработки)
- **Telegram-бот:**
  - aiogram 3

## Настройка и установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/your-username/toj_market.git
    cd toj_market
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    venv\Scripts\activate  # Для Windows
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Создайте файл `.env`** в корневой директории проекта и добавьте в него следующие переменные окружения:
    ```env
    SECRET_KEY='your-django-secret-key'
    DEBUG=True
    BOT_TOKEN='your-telegram-bot-token'
    BOT_USERNAME='YourBotUsername'
    ```
    **Примечание:** `EMAIL_HOST_PASSWORD` жестко закодирован в `server/settings.py`. Для продакшена рекомендуется перенести его в переменные окружения.

5.  **Примените миграции базы данных:**
    ```bash
    python manage.py migrate
    ```

6.  **Создайте суперпользователя:**
    ```bash
    python manage.py createsuperuser
    ```

## Запуск приложения

- **Запустите сервер для разработки:**
  ```bash
  python manage.py runserver
  ```
  Приложение будет доступно по адресу `http://127.0.0.1:8000/`.

- **Документация API (Swagger):**
  - `http://127.0.0.1:8000/swagger/`
  - `http://127.0.0.1:8000/redoc/`

## Запуск Telegram-бота

Вы можете запустить Telegram-бота одним из двух способов:

1.  **Как standalone-скрипт:**
    ```bash
    python bot.py
    ```

2.  **Через Django management command:**
    ```bash
    python manage.py runbot
    ```

## Структура проекта

```
toj_market/
├── accounts/       # Приложение для управления пользователями
├── market/         # Приложение для управления магазином
├── server/         # Настройки проекта Django
├── bot.py          # Логика Telegram-бота
├── manage.py       # Утилита командной строки Django
├── requirements.txt # Зависимости проекта
└── README.md       # Этот файл
```

---

<a name="en"></a>

# Toj Market (English)

Toj Market is a full-featured e-commerce platform built with Django and Django REST Framework. It provides a REST API for managing users, products, shops, and orders. The project also includes a Telegram bot for sellers to manage their shops on the go.

## Contents

- [Toj Market (Russian)](#ru)
- [Toj Market (English)](#toj-market-english)
  - [Contents](#contents)
  - [Features](#features)
  - [Technologies Used](#technologies-used)
  - [Setup and Installation](#setup-and-installation)
  - [Running the Application](#running-the-application)
  - [Running the Telegram Bot](#running-the-telegram-bot)
  - [Project Structure](#project-structure)

---

## Features

- **Authentication and User Management:** JWT authentication (access and refresh tokens), registration, login, user profile.
- **User Roles:** Admin, Buyer, Seller.
- **Shops:** Sellers can create and manage their shops.
- **Products:** CRUD operations for products with images, categories, discounts, and reviews.
- **Shopping Cart and Orders:** A complete shopping cart and order management system.
- **Search:** Search history.
- **REST API:** A full-fledged REST API with Swagger (OpenAPI) documentation.
- **Telegram Bot for Sellers:**
  - View and manage orders.
  - View and delete products.
  - View shop statistics.
  - Link a Telegram account with a website account.

## Technologies Used

- **Backend:**
  - Python 3
  - Django
  - Django REST Framework
  - Django Simple JWT
  - drf-yasg (Swagger)
- **Database:**
  - SQLite3 (for development)
- **Telegram Bot:**
  - aiogram 3

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/toj_market.git
    cd toj_market
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/macOS
    venv\Scripts\activate  # For Windows
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file** in the project root directory and add the following environment variables:
    ```env
    SECRET_KEY='your-django-secret-key'
    DEBUG=True
    BOT_TOKEN='your-telegram-bot-token'
    BOT_USERNAME='YourBotUsername'
    ```
    **Note:** The `EMAIL_HOST_PASSWORD` is hardcoded in `server/settings.py`. It is recommended to move it to environment variables for production.

5.  **Apply the database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

## Running the Application

- **Start the development server:**
  ```bash
  python manage.py runserver
  ```
  The application will be available at `http://127.0.0.1:8000/`.

- **API Documentation (Swagger):**
  - `http://127.0.0.1:8000/swagger/`
  - `http://127.0.0.1:8000/redoc/`

## Running the Telegram Bot

You can run the Telegram bot in one of two ways:

1.  **As a standalone script:**
    ```bash
    python bot.py
    ```

2.  **Via a Django management command:**
    ```bash
    python manage.py runbot
    ```

## Project Structure

```
toj_market/
├── accounts/       # User management app
├── market/         # Marketplace management app
├── server/         # Django project settings
├── bot.py          # Telegram bot logic
├── manage.py       # Django command-line utility
├── requirements.txt # Project dependencies
└── README.md       # This file
```
