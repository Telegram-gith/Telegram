from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase


async def get_product_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    products = await db.get_all_products()
    for i, product in enumerate(sorted(products, key=lambda p: p.id)):
        kb.button(text=f"{i+1}. {product.name}", callback_data=f"get_product_{product.id}")
    kb.adjust(2)
    return kb.as_markup()


async def return_product_list_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться к списку продуктов", callback_data=f"return_product_list")
    kb.button(text="Вернуться в главное меню", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()
