from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Category


async def category_inline_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    cats = await db.get_table(Category)
    for cat in cats:
        kb.button(text=f"{cat.name}", callback_data=f'select_{cat.name}_{cat.id}')
    kb.adjust(1)
    return kb.as_markup()


async def cancel_category_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить', callback_data='cancel_category')
    kb.adjust(1)
    return kb.as_markup()
