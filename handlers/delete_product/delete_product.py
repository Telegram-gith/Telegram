from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from handlers.start.start_kb import start_kb
from database.Database import DataBase
from handlers.delete_product.delete_product_kb import delete_product_kb, callback_product_kb
from filters.check_admin import CheckAdmin, CheckSuperAdmin
from handlers.catalog.catalog import format_price

delete_router = Router()


# Обработчик команды /delete_product
@delete_router.message(or_f(F.text.lower() == '/удалить продукт', F.text.lower() == 'удалить продукт'),
                       or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def delete_product_list(message: Message, bot: Bot):
    db = DataBase()
    products = await db.get_all_products()
    if products:
        await bot.send_message(message.from_user.id, 'Выберите продукт, который вы хотите удалить.',
                               reply_markup=await callback_product_kb())
    else:
        await message.answer("Нет продуктов, доступных для удаления.")


# Обработчик выбора продукта по ID
@delete_router.callback_query(F.data.startswith('delete_product_'))
async def select_product(call: CallbackQuery):
    product_id = int(call.data.split("_")[-1])
    db = DataBase()
    product = await db.get_product_one(product_id)
    if product:
        formatted_price = format_price(product.price)
        # Показываем карточку с продуктом и кнопки Delete и Cancel
        await call.message.answer(
            f"Информация о продукте:\n\n"
            f"Имя: {product.name}\n"
            f"Описание: {product.description}\n"
            f"Количество: {product.quantity}\n"
            f"Цена: {formatted_price}" + " сум",
            reply_markup=await delete_product_kb(product_id),
        )
    else:
        await call.message.answer("Продукт не найден.")
    await call.answer()


# Обработчик нажатий кнопок Delete и Cancel
@delete_router.callback_query(F.data.startswith("delete_"))
async def callback_delete_product(call: CallbackQuery):
    product_id = int(call.data.split("_")[-1])
    try:
        db = DataBase()
        await db.delete_product(product_id)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer("Продукт успешно удален!")
    except Exception as e:
        print(e)
        await call.message.answer("Не удалось удалить продукт. Пожалуйста, попробуйте снова.")
    await call.answer()


@delete_router.callback_query(F.data.startswith("cancel_delete"))
async def product_delete_cancel(call: CallbackQuery):
    db = DataBase()
    lang = db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Операция отменена.", reply_markup=start_kb(lang))
    await call.answer()
