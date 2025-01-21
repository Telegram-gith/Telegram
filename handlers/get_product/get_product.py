from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from handlers.start.start_kb import start_kb
from database.Database import DataBase
from handlers.get_product.get_product_kb import get_product_kb, return_product_list_kb
from filters.check_admin import CheckAdmin, CheckSuperAdmin
from handlers.catalog.catalog import format_price

get_router = Router()


# Handler to get the product list
@get_router.message(or_f(F.text.lower() == '/список продуктов', F.text.lower() == 'список продуктов'), or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def get_product_list(message: Message, bot: Bot):
    db = DataBase()
    products = await db.get_all_products()
    if products:
        await bot.send_message(
            message.from_user.id,
            'Выберите продукт, который вы хотите увидеть: ',
            reply_markup=await get_product_kb()
        )
    else:
        await message.answer("Нет доступных продуктов.")


# Handler to view product details
@get_router.callback_query(F.data.startswith("get_product_"))
async def view_product_details(call: CallbackQuery):
    product_id = int(call.data.split("_")[-1])
    db = DataBase()
    # Get product details
    product = await db.get_product_one(product_id)
    if product:
        formatted_price = format_price(product.price)
        # Send product details
        await call.message.edit_text(
            f"Подробная информация о продукте: \n\n"
            f"Название {product.name}\n"
            f"Описание: {product.description}\n"
            f"Количество: {product.quantity}\n"
            f"Цена: {formatted_price}" + " сум" + '\n',
            reply_markup=await return_product_list_kb()
        )
    else:
        await call.message.edit_text("Товар не найден.")
    await call.answer()


# Handler to return to the product list
@get_router.callback_query(F.data == 'return_product_list')
async def return_to_product_list(call: CallbackQuery):
    db = DataBase()
    products = await db.get_all_products()
    if products:
        await call.message.edit_text(
            "Выберите продукт для просмотра подробной информации: ",
            reply_markup=await get_product_kb()
        )
    else:
        await call.message.edit_text("Нет доступных продуктов.")
    await call.answer()


# Handler to return to the main menu
@get_router.callback_query(F.data == 'main_menu')
async def return_to_main_menu(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.answer(
        "Вернулись в главное меню.",
        reply_markup=start_kb(lang)
    )
    await call.answer()
