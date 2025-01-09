from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Category
from core.translation import _


async def category_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    cats = await db.get_table(Category)
    for cat in cats:
        kb.button(text=f"{cat.name}", callback_data=f'cat_select_{cat.name}_{cat.id}')
    kb.adjust(1)
    return kb.as_markup()


async def cancel_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=_('Отменить', lang), callback_data=f'cancel')
    kb.adjust(1)
    return kb.as_markup()
