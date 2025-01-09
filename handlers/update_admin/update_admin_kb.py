from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Admins


async def admin_inline_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    ads = await db.get_table(Admins)
    for ad in sorted(ads, key=lambda a: a.id):
        kb.button(text=f"{ad.username}", callback_data=f'select_{ad.username}_{ad.id}')
    kb.adjust(1)
    return kb.as_markup()


async def cancel_admin_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Отменить', callback_data='cancel_update_admin')
    kb.adjust(1)
    return kb.as_markup()
