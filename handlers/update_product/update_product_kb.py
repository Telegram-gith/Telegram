from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Category


async def product_inline_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    products = await db.get_all_products()
    for product in sorted(products, key=lambda p: p.id):
        kb.button(text=f"{product.id}. {product.name}", callback_data=f"update_product_{product.id}")
    kb.adjust(2)
    return kb.as_markup()


async def category_inline_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    cats = await db.get_table(Category)
    for cat in cats:
        kb.button(text=f"{cat.name}", callback_data=f'cat_select_update_{cat.name}_{cat.id}')
    kb.adjust(1)
    return kb.as_markup()


async def cancel_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить', callback_data=f'cancel')
    kb.adjust(1)
    return kb.as_markup()
