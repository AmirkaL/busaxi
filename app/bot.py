# app/bot.py
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from . import config
import logging

logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

@router.message(CommandStart())
async def start_command(message: Message, command: CommandObject):
    """
    Обработчик /start, который умеет принимать параметры (deep link) от NFC-меток.
    """
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    
    # **ИСПРАВЛЕНИЕ:** Используем command.args для безопасного получения параметра.
    # Если команда была /start amir_temur, command.args будет "amir_temur"
    # Если команда была просто /start, command.args будет None
    deep_link_args = command.args

    web_app_url = config.HOST_LINK
    if deep_link_args:
        web_app_url += f"/#{deep_link_args}"
        logger.info(f"Обнаружен deep link: '{deep_link_args}'. URL для WebApp: {web_app_url}")
    else:
        logger.info("Deep link не обнаружен.")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Открыть BuSaXi",
                web_app=WebAppInfo(url=web_app_url)
            )
        ]]
    )
    await message.answer(
        "Добро пожаловать в BuSaXi! Нажмите на кнопку ниже, чтобы открыть приложение:",
        reply_markup=keyboard
    )