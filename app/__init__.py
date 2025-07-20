# app/__init__.py --- ПОЛНЫЙ И ИСПРАВЛЕННЫЙ КОД

from flask import Flask
import logging
import schedule
import time
from threading import Thread
from . import config  # config теперь знает о нашем переключателе
from .services import init_db, update_all_news, update_all_exhibitions, update_all_museums, update_all_routes, \
    update_all_catalog_items

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(config)


def run_scheduler():
    logger.info("Планировщик фоновых задач запущен.")
    # Парсинг по расписанию мы оставляем включенным, он не мешает быстрому запуску.
    # Он будет выполняться только раз в час в фоновом режиме.
    schedule.every(1).hours.do(update_all_news)
    schedule.every(1).hours.do(update_all_exhibitions)
    schedule.every(1).hours.do(update_all_museums)
    schedule.every(1).hours.do(update_all_routes)
    schedule.every(1).hours.do(update_all_catalog_items)
    while True:
        schedule.run_pending()
        time.sleep(60)


def start_background_tasks():
    logger.info("Инициализация БД...")
    init_db()

    # *** ИСПОЛЬЗУЕМ НАШ ПЕРЕКЛЮЧАТЕЛЬ ***
    if config.ENABLE_PARSING_ON_START:
        logger.info("Первичный парсинг ВКЛЮЧЕН. Запускаю сбор данных...")
        update_all_news()
        update_all_exhibitions()
        update_all_museums()
        update_all_routes()
        update_all_catalog_items()
        logger.info("Первичный парсинг завершен.")
    else:
        logger.warning("Первичный парсинг ВЫКЛЮЧЕН (согласно настройке в .env). Пропускаю...")

    # Фоновый планировщик запускается в любом случае
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


from . import views