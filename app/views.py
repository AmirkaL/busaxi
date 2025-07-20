# app/views.py
from flask import render_template, jsonify, request, abort  # <-- ИСПРАВЛЕНИЕ: ДОБАВЛЕН `abort`
import base64
from . import app
from . import services

import logging

logger = logging.getLogger(__name__)

# ПРОСТАЯ БАЗА ДАННЫХ ДЛЯ ВИДЕО, ПЕРЕМЕЩАЕМ ЕЕ СЮДА
VIDEO_DATABASE = {
    'amir_temur': {
        'ru': {'title': 'Цитата Амира Темура', 'video_path': '/static/videos/amir_temur_monologue.mp4'},
        'uz': {'title': 'Amir Temur iqtibosi', 'video_path': '/static/videos/amir_temur_monologue_uz.mp4'},
        'en': {'title': 'Quote by Amir Temur', 'video_path': '/static/videos/amir_temur_monologue_en.mp4'}
    }
}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/news')
def get_news_api():
    lang = request.args.get('lang', 'ru')
    return jsonify(services.get_all_news(lang=lang))

# *** НОВЫЙ ЭНДПОИНТ ДЛЯ ВИДЕО ***
@app.route('/video/<string:video_id>')
def video_page(video_id):
    lang = request.accept_languages.best_match(['ru', 'uz', 'en']) or 'ru'
    video_data = VIDEO_DATABASE.get(video_id)
    if not video_data:
        abort(404)
    lang_specific_data = video_data.get(lang, video_data['ru'])
    return render_template(
        'video_page.html',
        title=lang_specific_data['title'],
        video_url=lang_specific_data['video_path'],
        VIDEO_DATABASE=VIDEO_DATABASE
    )

@app.route('/api/exhibitions')
def get_exhibitions_api():
    lang = request.args.get('lang', 'ru')
    return jsonify(services.get_all_exhibitions(lang=lang))


@app.route('/api/museums')
def get_museums_api():
    lang = request.args.get('lang', 'ru')
    return jsonify(services.get_all_museums(lang=lang))


# *** НОВЫЙ МАРШРУТ ДЛЯ ОТРИСОВКИ КАРТЫ ***
@app.route('/map.html')
def map_page():
    return render_template('map.html')

# *** НОВЫЙ API-ЭНДПОИНТ ДЛЯ МАРШРУТОВ ***
@app.route('/api/routes')
def get_routes_api():
    lang = request.args.get('lang', 'ru')
    try:
        routes_data = services.get_all_routes(lang=lang)
        return jsonify(routes_data)
    except Exception as e:
        return jsonify({"error": f"Не удалось получить маршруты: {e}"}), 500

@app.route('/api/catalog')
def get_catalog_api():
    """API для получения элементов каталога с фильтрацией."""
    lang = request.args.get('lang', 'ru')
    category = request.args.get('category', 'all')
    try:
        catalog_data = services.get_catalog_items(lang=lang, category=category)
        return jsonify(catalog_data)
    except Exception as e:
        return jsonify({"error": f"Не удалось получить элементы каталога: {e}"}), 500


# *** НОВЫЙ ЭНДПОИНТ ДЛЯ ПОЛУЧЕНИЯ ДЕТАЛЕЙ ***
@app.route('/api/catalog_item')
def get_catalog_item_api():
    lang = request.args.get('lang', 'ru')
    item_id = request.args.get('id', None)

    if not item_id:
        return jsonify({"error": "ID объекта не указан"}), 400

    try:
        details_data = services.get_catalog_item_details(item_id=item_id, lang=lang)
        if details_data:
            return jsonify(details_data)
        else:
            return jsonify({"error": "Объект не найден"}), 404
    except Exception as e:
        return jsonify({"error": f"Не удалось получить детали объекта: {e}"}), 500
        
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image_api():
    """API-эндпоинт для анализа изображения с помощью Gemini."""
    if 'image' not in request.json:
        return jsonify({"error": "Изображение не найдено"}), 400

    image_b64 = request.json['image']
    lang = request.json.get('lang', 'ru')
    
    prompts = {
        'ru': "Что изображено на этой фотографии?",
        'uz': "Bu fotosuratda nima tasvirlangan?",
        'en': "What is depicted in this photograph?"
    }
    user_prompt = prompts.get(lang, prompts['ru'])

    try:
        # **ИЗМЕНЕНИЕ**: Теперь мы передаем строку base64 напрямую
        description = services.analyze_image_with_gemini(image_b64, user_prompt, lang)
        
        return jsonify({"description": description})
    except Exception as e:
        logger.error(f"Ошибка на эндпоинте /api/analyze-image: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера при анализе"}), 500