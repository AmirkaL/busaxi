import sqlite3
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import traceback
import re
import time
from . import config

# ИМПОРТЫ, НЕОБХОДИМЫЕ ДЛЯ GEMINI И ПРОКСИ
import google.generativeai as genai
import socks
import socket


logger = logging.getLogger(__name__)
SUPPORTED_LANGUAGES = ['ru', 'uz', 'en']


def get_db_connection():
    conn = sqlite3.connect(config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализирует БД, добавляя таблицу для маршрутов."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS exhibitions (id TEXT NOT NULL, lang TEXT NOT NULL, title TEXT, published_at TEXT, description TEXT, url TEXT, image_url TEXT, date_range TEXT, location TEXT, PRIMARY KEY (id, lang))''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY AUTOINCREMENT, lang TEXT NOT NULL, title TEXT, image_url TEXT, date TEXT)''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS museums (id TEXT NOT NULL, lang TEXT NOT NULL, title TEXT, url TEXT, image_url TEXT, PRIMARY KEY (id, lang))''')

        # *** НОВАЯ ТАБЛИЦА ДЛЯ МАРШРУТОВ ***
        cursor.execute('''CREATE TABLE IF NOT EXISTS routes (
                           id TEXT NOT NULL,
                           lang TEXT NOT NULL,
                           title TEXT,
                           url TEXT,
                           image_url TEXT,
                           PRIMARY KEY (id, lang)
                       )''')

        # *** НОВАЯ ТАБЛИЦА ДЛЯ КАТАЛОГА ***
        cursor.execute('''CREATE TABLE IF NOT EXISTS catalog_items (
                               id TEXT NOT NULL,
                               lang TEXT NOT NULL,
                               category TEXT NOT NULL,
                               title TEXT,
                               url TEXT,
                               image_url TEXT,
                               PRIMARY KEY (id, lang, category)
                           )''')

        conn.commit()
        logger.info("База данных успешно инициализирована с таблицей каталога.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
    finally:
        if conn: conn.close()


def scrape_news(lang='ru'):
    """Парсит новости для УКАЗАННОГО языка с учетом особенностей URL."""
    try:
        if lang == 'en':
            # Исправляем URL для английской версии society.uz
            url = "https://society.uz/news/news"
        elif lang in ['ru', 'uz']:
            url = f"https://society.uz/{lang}/news/news"
        else:
            logger.warning(f"Парсинг новостей для языка '{lang}' не поддерживается. Пропускаем.")
            return

        headers = {"User-Agent": "HeritageVoiceApp/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            logger.warning(f"Страница новостей для языка '{lang}' не найдена (404). Пропускаем.")
            return
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        news_cards = soup.find_all("a", class_="news-card")[:4]
        if not news_cards:
            logger.warning(f"На странице новостей для языка '{lang}' не найдено карточек новостей.")
            return

        news_data = []
        for card in news_cards:
            title = card.find("h3", class_="news-card-title").text.strip()
            image_url = card.find("img")["src"] if card.find("img") and card.find("img").has_attr("src") else ""
            date_time = card.find("time")["datetime"] if card.find("time") and card.find("time").has_attr(
                "datetime") else datetime.now().isoformat()
            news_data.append({"title": title, "image_url": image_url, "date": date_time})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM news WHERE lang = ?", (lang,))
        for news_item in news_data:
            cursor.execute("INSERT INTO news (title, image_url, date, lang) VALUES (?, ?, ?, ?)",
                           (news_item["title"], news_item["image_url"], news_item["date"], lang))
        conn.commit()
        conn.close()
        logger.info(f"Новости ({lang}) успешно обновлены: {len(news_data)} записей.")

    except Exception as e:
        logger.error(f"Неизвестная ошибка при парсинге новостей ({lang}): {e}\n{traceback.format_exc()}")


def scrape_exhibitions(lang='ru'):
    """Парсит выставки для УКАЗАННОГО языка, с резервной логикой для 'en'."""
    try:
        source_lang = 'ru' if lang == 'en' else lang
        url = f"https://www.afisha.uz/{source_lang}/exhibitions"
        headers = {"User-Agent": "HeritageVoiceApp/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            logger.warning(
                f"Исходная страница выставок для '{source_lang}' не найдена (404). Пропускаем язык '{lang}'.")
            return
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        exhibition_links = soup.select('a[href*="/exhibitions/"]')
        exhibitions_data = []
        for link_tag in exhibition_links:
            block = link_tag.find('article')
            if not block: continue
            title = block.find('h3').get_text(strip=True) if block.find('h3') else 'Без названия'
            date_text = block.select_one('li:first-child span').get_text(strip=True) if block.select_one(
                'li:first-child span') else None
            location = block.select_one('li:last-child').get_text(strip=True) if block.select_one(
                'li:last-child') else None
            image_url = block.find('img')['src'] if block.find('img') and block.find('img').has_attr('src') else None
            link_href = link_tag['href']
            exhibition_id = link_href.split('/')[-1] if link_href else str(hash(title))
            full_image_url = f"https://www.afisha.uz{image_url}" if image_url and not image_url.startswith(
                'http') else image_url
            full_link_url = f"https://www.afisha.uz{link_href}" if link_href and not link_href.startswith(
                'http') else link_href
            exhibitions_data.append(
                {'id': exhibition_id, 'title': title, 'published_at': datetime.now().isoformat(), 'description': '',
                 'url': full_link_url, 'image_url': full_image_url, 'date_range': date_text, 'location': location})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exhibitions WHERE lang = ?", (lang,))
        for ex in exhibitions_data:
            cursor.execute(
                '''INSERT OR REPLACE INTO exhibitions (id, lang, title, published_at, description, url, image_url, date_range, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (ex['id'], lang, ex['title'], ex['published_at'], ex['description'], ex['url'], ex['image_url'],
                 ex['date_range'], ex['location']))
        conn.commit()
        conn.close()

        if lang == 'en':
            logger.info(
                f"Выставки (en) успешно обновлены, используя 'ru' как источник: {len(exhibitions_data)} записей.")
        else:
            logger.info(f"Выставки ({lang}) успешно обновлены: {len(exhibitions_data)} записей.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при парсинге выставок ({lang}): {e}\n{traceback.format_exc()}")


def scrape_museums(lang='ru'):
    """Парсит категории музеев с uzbekistan.travel для указанного языка."""
    try:
        url = f"https://uzbekistan.travel/{lang}/c/muzei/"
        headers = {"User-Agent": "HeritageVoiceApp/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            logger.warning(f"Страница музеев для языка '{lang}' не найдена (404). Пропускаем.")
            return
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        museum_items = soup.select('.blog-list.pod_razdels a.blog_item')
        museums_data = []
        for item in museum_items:
            title_tag = item.select_one('h3._title')
            style_attr_tag = item.select_one('.blog_item_top')
            if not title_tag or not style_attr_tag or not item.has_attr('href'):
                continue
            title = title_tag.get_text(strip=True)
            relative_url = item['href']
            style_attr = style_attr_tag.get('style', '')
            match = re.search(r"url\((.*?)\)", style_attr)
            image_url = match.group(1).strip("'\"") if match else None
            if not image_url: continue
            museum_id = relative_url.strip('/').split('/')[-1]
            full_url = f"https://uzbekistan.travel{relative_url}"
            museums_data.append({'id': museum_id, 'title': title, 'url': full_url, 'image_url': image_url})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM museums WHERE lang = ?", (lang,))
        for museum in museums_data:
            cursor.execute(
                '''INSERT OR REPLACE INTO museums (id, lang, title, url, image_url) VALUES (?, ?, ?, ?, ?)''',
                (museum['id'], lang, museum['title'], museum['url'], museum['image_url']))
        conn.commit()
        conn.close()
        logger.info(f"Музеи ({lang}) успешно обновлены: {len(museums_data)} записей.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при парсинге музеев ({lang}): {e}\n{traceback.format_exc()}")


def scrape_routes(lang='ru'):
    """Парсит маршруты с uzbekistan.travel для указанного языка."""
    try:
        url = f"https://uzbekistan.travel/{lang}/c/topovye-marshruty/"
        headers = {"User-Agent": "HeritageVoiceApp/1.0"}

        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            logger.warning(f"Страница маршрутов для языка '{lang}' не найдена (404). Пропускаем.")
            return
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        route_items = soup.select('div.blog-list a.blog_item')
        routes_data = []

        for item in route_items:
            title_tag = item.select_one('h3._title')
            style_attr_tag = item.select_one('.blog_item_top')
            if not title_tag or not style_attr_tag or not item.has_attr('href'):
                continue

            title = title_tag.get_text(strip=True)
            relative_url = item['href']

            style_attr = style_attr_tag.get('style', '')
            match = re.search(r"url\((.*?)\)", style_attr)
            image_url = match.group(1).strip("'\"") if match else None

            if not image_url: continue

            route_id = relative_url.strip('/').split('/')[-1]
            full_url = f"https://uzbekistan.travel{relative_url}"

            routes_data.append({'id': route_id, 'title': title, 'url': full_url, 'image_url': image_url})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM routes WHERE lang = ?", (lang,))
        for route in routes_data:
            cursor.execute('''INSERT OR REPLACE INTO routes (id, lang, title, url, image_url)
                              VALUES (?, ?, ?, ?, ?)''',
                           (route['id'], lang, route['title'], route['url'], route['image_url']))
        conn.commit()
        conn.close()
        logger.info(f"Маршруты ({lang}) успешно обновлены: {len(routes_data)} записей.")

    except Exception as e:
        logger.error(f"Неизвестная ошибка при парсинге маршрутов ({lang}): {e}\n{traceback.format_exc()}")


def _parse_and_save_catalog_page(url_path: str, category: str, lang: str, conn: sqlite3.Connection):
    """Вспомогательная функция для парсинга одной страницы каталога."""
    try:
        full_url = f"https://uzbekistan.travel{url_path}"
        headers = {"User-Agent": "HeritageVoiceApp/1.0"}
        response = requests.get(full_url, headers=headers)
        if response.status_code == 404:
            logger.warning(f"Страница каталога '{category}' для языка '{lang}' не найдена: {full_url}")
            return
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('a.blog_item, a.destinations_item')
        if not items:
            logger.warning(f"На странице каталога '{category}' ({lang}) не найдено элементов.")
            return

        items_data = []
        for item in items:
            title_tag = item.select_one('h3._title, div._content h3')
            style_attr_tag = item if 'background-image' in item.get('style', '') else item.select_one(
                '.blog_item_top, .img')

            if not title_tag or not style_attr_tag or not item.has_attr('href'):
                continue

            title = title_tag.get_text(strip=True)
            relative_url = item['href']

            style_attr = style_attr_tag.get('style', '')
            match = re.search(r"url\((.*?)\)", style_attr)
            image_url = match.group(1).strip("'\"") if match else None

            if not image_url or not title or not relative_url:
                continue

            item_id = f"{category}_{relative_url.strip('/').split('/')[-1]}"
            full_url = f"https://uzbekistan.travel{relative_url}"
            items_data.append({'id': item_id, 'title': title, 'url': full_url, 'image_url': image_url})

        if items_data:
            cursor = conn.cursor()
            for item_data in items_data:
                cursor.execute(
                    '''INSERT OR REPLACE INTO catalog_items (id, lang, category, title, url, image_url)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (item_data['id'], lang, category, item_data['title'], item_data['url'], item_data['image_url'])
                )
            logger.info(f"Каталог '{category}' ({lang}) обновлен: {len(items_data)} записей.")

    except Exception as e:
        logger.error(f"Ошибка при парсинге каталога '{category}' ({lang}): {e}\n{traceback.format_exc()}")


def scrape_catalog_all(lang='ru'):
    """Основная функция для парсинга всех категорий каталога с правильными URL."""
    CATALOG_SOURCES = {
        'sights': {'ru': '/ru/c/dostoprimechatelnosti/', 'uz': '/uz/c/diqqatga-sazovor-joylar/',
                   'en': '/en/c/attractions/'},
        'cities': {'ru': '/ru/i/goroda-uzbekistana/', 'uz': '/uz/ozbekiston-shaharlari/',
                   'en': '/en/i/uzbekistan-cities/'},
        'cuisine': {'ru': '/ru/c/uzbekskaya-kuhnya/', 'uz': '/uz/c/ozbek-taomlari/', 'en': '/en/c/uzbek-cuisine/'},
    }

    conn = get_db_connection()
    try:
        categories_to_clear = tuple(CATALOG_SOURCES.keys())
        query_placeholder = ','.join(['?'] * len(categories_to_clear))
        conn.execute(f"DELETE FROM catalog_items WHERE lang = ? AND category IN ({query_placeholder})",
                     (lang, *categories_to_clear))

        for category, lang_paths in CATALOG_SOURCES.items():
            if lang in lang_paths:
                _parse_and_save_catalog_page(lang_paths[lang], category, lang, conn)
                time.sleep(1)
        conn.commit()
    finally:
        if conn: conn.close()


def get_catalog_item_details(item_id: str, lang: str):
    """
    Парсит детальную страницу объекта с uzbekistan.travel.
    Это новая функция, необходимая для детального просмотра.
    """
    conn = get_db_connection()
    item_row = conn.execute("SELECT url FROM catalog_items WHERE id = ? AND lang = ?", (item_id, lang)).fetchone()
    conn.close()

    if not item_row or not item_row['url']:
        logger.warning(f"URL для объекта id={item_id} ({lang}) не найден в БД.")
        return None

    url = item_row['url']
    headers = {"User-Agent": "HeritageVoiceApp/1.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Заголовок и подзаголовок
        title = soup.select_one('h1.page-title').get_text(strip=True) if soup.select_one(
            'h1.page-title') else "Заголовок не найден"
        subtitle = soup.select_one('div.top_page-subtitle').get_text(strip=True) if soup.select_one(
            'div.top_page-subtitle') else None

        # Основное фото (фоновое изображение хедера)
        main_photo_style = soup.select_one('div.top_page.inner-page').get('style', '') if soup.select_one(
            'div.top_page.inner-page') else ''
        main_photo_match = re.search(r"url\((.*?)\)", main_photo_style)
        main_photo_url = main_photo_match.group(1).strip("'\"") if main_photo_match else None

        # Основной контент (текст)
        content_html_element = soup.select_one('div.post-content.content')
        if content_html_element:
            # Очищаем контент от ненужных блоков (например, формы)
            for el in content_html_element.select('.contact_form_inner_block, .tags-list'):
                el.decompose()
            content_html = str(content_html_element)
        else:
            content_html = "<p>Описание не найдено.</p>"

        # Галерея
        image_gallery = []
        gallery_items = soup.select('.element-gallery-wrapper .gallery-item a, .photo-gallery_item a')
        for item in gallery_items:
            img_url = item.get('href')
            if img_url:
                image_gallery.append(img_url)

        return {
            'id': item_id,
            'title': title,
            'subtitle': subtitle,
            'image_url': main_photo_url,
            'content_html': content_html,
            'image_gallery': image_gallery,
        }

    except Exception as e:
        logger.error(f"Не удалось получить детали для объекта {item_id} с URL {url}: {e}\n{traceback.format_exc()}")
        return None


def update_all_news():
    for lang in SUPPORTED_LANGUAGES:
        scrape_news(lang)
        time.sleep(1)


def update_all_exhibitions():
    for lang in SUPPORTED_LANGUAGES:
        scrape_exhibitions(lang)
        time.sleep(1)


def update_all_museums():
    for lang in SUPPORTED_LANGUAGES:
        scrape_museums(lang)
        time.sleep(1)


def update_all_routes():
    for lang in SUPPORTED_LANGUAGES:
        scrape_routes(lang)
        time.sleep(1)


def update_all_catalog_items():
    for lang in SUPPORTED_LANGUAGES:
        scrape_catalog_all(lang)


def get_all_news(lang='ru'):
    conn = get_db_connection()
    news = conn.execute("SELECT title, image_url, date FROM news WHERE lang = ? ORDER BY date DESC", (lang,)).fetchall()
    conn.close()
    return [dict(row) for row in news]


def get_all_exhibitions(lang='ru'):
    conn = get_db_connection()
    exhibitions = conn.execute("SELECT * FROM exhibitions WHERE lang = ? ORDER BY published_at DESC LIMIT 20",
                               (lang,)).fetchall()
    conn.close()
    return [dict(row) for row in exhibitions]


def get_all_museums(lang='ru'):
    conn = get_db_connection()
    museums = conn.execute("SELECT * FROM museums WHERE lang = ?", (lang,)).fetchall()
    conn.close()
    return [dict(row) for row in museums]


def get_all_routes(lang='ru'):
    conn = get_db_connection()
    routes = conn.execute("SELECT * FROM routes WHERE lang = ?", (lang,)).fetchall()
    conn.close()
    return [dict(row) for row in routes]


def get_catalog_items(lang='ru', category=None):
    conn = get_db_connection()
    if category and category != 'all':
        items = conn.execute("SELECT * FROM catalog_items WHERE lang = ? AND category = ?", (lang, category)).fetchall()
    else:
        items = conn.execute("SELECT * FROM catalog_items WHERE lang = ?", (lang,)).fetchall()
    conn.close()
    result = [dict(row) for row in items]
    logger.debug(f"Возвращено {len(result)} элементов для категории '{category}' ({lang})")
    return result
    

import google.generativeai as genai

# Простая одноразовая конфигурация Gemini при старте приложения
try:
    if config.GEMINI_API_KEY:
        genai.configure(api_key=config.GEMINI_API_KEY)
    else:
        logger.warning("Ключ GEMINI_API_KEY не найден в .env")
except Exception as e:
    logger.error(f"Не удалось сконфигурировать Gemini: {e}")

SYSTEM_PROMPT = """
Ты — эрудированный и увлекательный гид по искусству и истории культурного наследия Узбекистана.
Твоя задача — проанализировать изображение музейного экспоната и предоставить исчерпывающую, но легко читаемую информацию.

Ответ должен быть в формате HTML единым блоком кода, БЕЗ ```html``` В НАЧАЛЕ И В КОНЦЕ.
Структура ответа:

1.  **Название:** В теге `<h3>`. Например: `<h3>Керамический кувшин</h3>`.
2.  **Период и Культура:** В теге `<p>`. Используй `<b>` для заголовка. Например: `<p><b>Период:</b> X-XI вв., эпоха Саманидов</p>`.
3.  **Описание:** В теге `<p>`. Используй `<b>` для заголовка. Например: `<p><b>Описание:</b> ...</p>`.
4.  **Исторический контекст:** В теге `<p>`. Используй `<b>` для заголовка.
5.  **Интересный факт:** В теге `<p>`. Используй `<b>` для заголовка.

Правила:
- Весь ответ должен быть единым HTML-блоком.
- Будь уверен в ответах. Используй "предположительно", если не уверен.
- Не упоминай, что ты — AI.
- Ответ должен быть на языке пользовательского запроса.
"""

def analyze_image_with_gemini(image_data: str, user_prompt: str, lang: str = 'ru') -> str:
    """Отправляет изображение в Gemini REST API и возвращает HTML-описание."""
    
    if not config.GEMINI_API_KEY or not config.PROXY_URL:
        return "<p>Сервис AI временно недоступен.</p>"

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={config.GEMINI_API_KEY}"
    lang_map = {'ru': 'русском', 'uz': 'узбекском', 'en': 'английском'}
    final_prompt = f"Язык ответа - {lang_map.get(lang, 'русском')}. {user_prompt}"

    request_body = { "contents": [{ "parts": [ {"text": SYSTEM_PROMPT}, {"text": final_prompt}, { "inline_data": { "mime_type": "image/jpeg", "data": image_data } } ] }] }
    proxies = { 'http': config.PROXY_URL, 'https': config.PROXY_URL }

    try:
        response = requests.post(api_url, json=request_body, proxies=proxies, timeout=60)
        response.raise_for_status()
        
        response_json = response.json()
        text_content = response_json['candidates'][0]['content']['parts'][0]['text']
        
        cleaned_html = text_content.strip().replace("```html", "").replace("```", "")
        logger.info("HTML-описание от Gemini успешно получено.")
        return cleaned_html

    except Exception as e:
        logger.error(f"Ошибка при запросе к Gemini: {e}")
        return "<p>Не удалось проанализировать изображение.</p>"