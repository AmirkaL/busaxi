# run.py

import logging
from aiohttp import web
from aiogram.types import Update
from aiohttp_wsgi import WSGIHandler

# Импортируем ключевые объекты из нашего пакета app
from app import app as flask_app, config, start_background_tasks
from app.bot import bot, dp  # Теперь bot и dp импортируются из исправленного bot.py

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Путь для вебхука, чтобы не писать его дважды
BOT_WEBHOOK_PATH = "/bot-webhook"


async def webhook_handler(request: web.Request) -> web.Response:
    """
    Обработчик, который принимает обновления от Telegram,
    валидирует их и передает в диспетчер для aiogram 3.x.
    """
    update_data = await request.json()
    update = Update.model_validate(update_data, context={"bot": bot})

    # "Скармливаем" обновление диспетчеру
    await dp.feed_update(bot=bot, update=update)

    return web.Response()


async def on_startup(app_instance: web.Application):
    """Выполняется при старте сервера."""
    webhook_url = f"{config.HOST_LINK}{BOT_WEBHOOK_PATH}"

    try:
        await bot.set_webhook(
            url=webhook_url,
            allowed_updates=dp.resolve_used_update_types()
        )
        logger.info(f"Вебхук успешно установлен на: {webhook_url}")
    except Exception as e:
        logger.error(f"Ошибка установки вебхука: {e}")

    # Запускаем наши фоновые задачи
    start_background_tasks()


async def on_shutdown(app_instance: web.Application):
    """Выполняется при остановке сервера."""
    logger.warning("Сервер останавливается... Удаляем вебхук.")
    await bot.delete_webhook()
    await dp.storage.close()
    logger.info("Вебхук успешно удален.")

# *** ГЛАВНОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ ***
# Создаем приложение aiohttp на глобальном уровне, чтобы Gunicorn мог его найти
aiohttp_app = web.Application()

# Регистрируем все обработчики
aiohttp_app.router.add_post(BOT_WEBHOOK_PATH, webhook_handler)
aiohttp_app.on_startup.append(on_startup)
aiohttp_app.on_shutdown.append(on_shutdown)

# "Прикручиваем" наше Flask-приложение
wsgi_handler = WSGIHandler(flask_app)
aiohttp_app.router.add_route('*', '/{path_info:.*}', wsgi_handler)

def main():
    """Эта функция теперь ТОЛЬКО запускает уже сконфигурированное приложение."""
    logger.info("Запуск веб-сервера на 0.0.0.0:8080 (локальный режим)")
    web.run_app(aiohttp_app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    # Этот блок выполняется, только если вы запускаете файл напрямую (`python run.py`)
    # Gunicorn его не выполняет, а импортирует aiohttp_app выше.
    main()