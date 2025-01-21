from aiogram import Dispatcher, Bot
import asyncio
import os
from dotenv import load_dotenv
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from core.menu import set_commands
from database.Database import DataBase

# Импорт обработчиков Telegram-бота
from handlers.start.start import start_router
from handlers.create_product.create_product import create_route
from handlers.catalog.catalog import catalog_router
from handlers.basket.basket import basket_router
from handlers.order.order import order_router
from handlers.update_product.update_product import update_route
from handlers.delete_product.delete_product import delete_router
from handlers.get_product.get_product import get_router
from handlers.create_category.create_category import create_category_router
from handlers.update_category.update_category import update_category_router
from handlers.delete_category.delete_category import delete_category_router
from handlers.get_category.get_category import get_category_router
from handlers.add_admin.add_admin import add_admin_router
from handlers.update_admin.update_admin import update_admin_router
from handlers.delete_admin.delete_admin import delete_admin_router
from handlers.get_admin.get_admin import get_admin_router
from handlers.delete_order.delete_order import delete_order_router
from handlers.update_language.update_language import language_router

# Загрузка переменных окружения
load_dotenv()
token = os.getenv("TOKEN_ID")

# Инициализация бота и диспетчера
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация обработчиков
dp.include_router(language_router)
dp.include_router(start_router)
dp.include_router(catalog_router)
dp.include_router(basket_router)
dp.include_router(order_router)
dp.include_router(create_category_router)
dp.include_router(update_category_router)
dp.include_router(delete_category_router)
dp.include_router(get_category_router)
dp.include_router(add_admin_router)
dp.include_router(update_admin_router)
dp.include_router(delete_admin_router)
dp.include_router(get_admin_router)
dp.include_router(create_route)
dp.include_router(update_route)
dp.include_router(delete_router)
dp.include_router(get_router)
dp.include_router(delete_order_router)


# Запуск бота и сервера
async def start():
    try:
        db = DataBase()
        await db.create_db()
        await set_commands(bot)
        # Старт бота
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # Запуск бота
    asyncio.run(start())  # Запуск бота
