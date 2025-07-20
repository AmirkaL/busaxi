# BuSaXi (A Soulful Axis of History)

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-MVP%20active-success)

> **Ожившая история Узбекистана в вашем смартфоне.**

**BuSaXi** — это инновационная мобильная платформа в формате Telegram Mini App, созданная для интерактивного изучения и популяризации культурного наследия Узбекистана. Мы превращаем традиционное знакомство с историей в увлекательное цифровое путешествие, доступное как туристам, так и местным жителям.

---

### 🏛️ О проекте

Проект решает проблему "статичности" культурного наследия. Туристы и молодежь часто сталкиваются с информационным вакуумом: данные в интернете разрознены, а таблички в музеях скучны. BuSaXi разрушает этот барьер, превращая смартфон каждого пользователя в интерактивный портал в историю.

Мы не просто каталог, мы — создатели опыта, который делает историю по-настоящему живой и захватывающей.

---

### ✨ Ключевые технологии и особенности

Наше решение построено на комбинации передовых технологий, которые создают уникальный пользовательский опыт:

*   🤖 **Интерактивный AI-гид:** Используя Computer Vision и Generative AI (Google Gemini), приложение распознает музейные экспонаты по фото и мгновенно предоставляет увлекательный рассказ о них на языке пользователя.
*   🎬 **"Ожившая история" с NFC:** Пользователь подносит телефон к NFC-метке у экспоната и на экране запускается видеомонолог исторической личности, созданный с помощью ИИ.
*   🗺️ **3D-погружение:** Интерактивные 3D-модели ключевых архитектурных ансамблей (например, площадь Регистан) позволяют "прогуляться" по объекту виртуально.
*   📰 **Единый агрегатор событий:** Платформа автоматически парсит и систематизирует актуальную информацию о выставках, музеях и туристических маршрутах со всего Узбекистана.
*   🌍 **Полная мультиязычность:** Интерфейс и весь контент, включая генерируемый ИИ, доступны на узбекском, русском и английском языках.
*   🚀 **Доступность без установки:** Реализация в формате Telegram Mini App обеспечивает мгновенный доступ без необходимости скачивать отдельное приложение.

---

### 💻 Технологический стек

| Категория | Технологии |
| :--- | :--- |
| **Бэкенд** | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white) ![Aiogram](https://img.shields.io/badge/Aiogram%203-2481CC) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=white) |
| **База данных** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white) |
| **Фронтенд** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) |
| **AI и 3D** | Google Gemini, Mapbox GL JS, Three.js |
| **Деплой** | ![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?logo=ubuntu&logoColor=white) ![Nginx](https://img.shields.io/badge/NGINX-009639?logo=nginx&logoColor=white) Systemd |

---

### 🚀 Запуск и развертывание

#### Локальный запуск
1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://your-repository-url.git
    cd BuSaXi
    ```
2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Создайте и настройте `.env` файл:**
    Скопируйте `.env.example` (если есть) или создайте новый файл `.env` в корне проекта со следующим содержимым:
    ```env
    BOT_TOKEN="ВАШ_ТОКЕН_БОТА"
    HOST_LINK="https://your-ngrok-link.ngrok-free.app" # Для локального теста с ngrok
    DATABASE_NAME="heritage.db"
    GEMINI_API_KEY="ВАШ_КЛЮЧ_GEMINI"
    PROXY_URL="socks5h://user:pass@host:port"
    ENABLE_INITIAL_SCRAPING="true"
    ```
5.  **Запустите приложение:**
    ```bash
    python run.py
    ```

#### Развертывание на VPS (Ubuntu)
Приложение разворачивается через связку **Nginx + Gunicorn + Systemd**.
1.  **Настройте Nginx** как реверс-прокси, который перенаправляет запросы с порта 443 (HTTPS) на ваше приложение.
2.  **Создайте Systemd-сервис** (`/etc/systemd/system/busaxi.service`), который будет управлять запуском Gunicorn.
    *Пример команды запуска в `.service` файле:*
    ```ini
    ExecStart=/var/www/busaxi/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 run:aiohttp_app --worker-class aiohttp.GunicornWebWorker
    ```
3.  Запустите и добавьте сервис в автозагрузку:
    ```bash
    systemctl start busaxi
    systemctl enable busaxi
    ```

---


### 🗺️ Дорожная карта

-   [x] **MVP:** Запуск платформы с парсингом новостей, выставок, музеев и маршрутов.
-   [x] **Интеграция AI:** Внедрение AI-гида для распознавания экспонатов.
-   [x] **Интеграция 3D/NFC:** Добавление 3D-карты и логики "ожившей истории" с NFC.
-   [ ] **Пилотный проект:** Партнерство с первым музеем для полной оцифровки коллекции и установки NFC-меток.
-   [ ] **Расширение каталога:** Добавление новых категорий (ремесла, природа) и детальных статей.
-   [ ] **Геймификация:** Внедрение викторин и системы достижений для пользователей.
-   [ ] **Запуск B2B/B2G платформы:** Создание SaaS-решения для музеев и государственных туристических организаций.

---

### 📬 Контакты

Амир – Lead Developer – amirlatipov@inbox.ru

Ссылка на проект: [https://t.me/BuSaXiBot]
