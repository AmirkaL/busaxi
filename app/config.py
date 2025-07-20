import os
from dotenv import load_dotenv

# Загружает переменные из файла .env в окружение
load_dotenv()

# Безопасно получаем переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
HOST_LINK = os.getenv("HOST_LINK")
DATABASE_NAME = os.getenv("DATABASE_NAME", "heritage.db") # Значение по умолчанию

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL")

# *** ДОБАВЛЯЕМ ЧТЕНИЕ НОВОЙ ПЕРЕМЕННОЙ ***
# .lower() in ('true', '1', 't') - это надежный способ прочитать булево значение
ENABLE_PARSING_ON_START = os.getenv('ENABLE_PARSING_ON_START', 'False').lower() in ('true', '1', 't')

# Проверка, что обязательные переменные установлены
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN. Убедитесь, что он задан в .env файле.")
if not HOST_LINK:
    raise ValueError("Не найден HOST_LINK. Убедитесь, что он задан в .env файле.")