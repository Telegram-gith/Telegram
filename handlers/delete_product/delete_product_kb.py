from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase


async def callback_product_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    products = await db.get_all_products()
    for i, product in enumerate(sorted(products, key=lambda p: p.id)):
        kb.button(text=f"{i+1}. {product.name}", callback_data=f"delete_product_{product.id}")
    kb.adjust(2)
    return kb.as_markup()


async def delete_product_kb(product_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Удалить", callback_data=f"delete_{product_id}")
    kb.button(text="Отменить", callback_data="cancel_delete")
    kb.adjust(2)
    return kb.as_markup()
