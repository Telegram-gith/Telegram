from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Admins


async def callback_admin_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    admins = await db.get_table(Admins)  # Ensure you have this method
    for i, admin in enumerate(sorted(admins, key=lambda a: a.id)):
        kb.button(text=f"{i+1}. {admin.username}", callback_data=f"delete_admin_{admin.id}")
    kb.adjust(2)
    return kb.as_markup()


async def delete_admin_kb(admin_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Удалить", callback_data=f"delete_ad_{admin_id}")
    kb.button(text="Отменить", callback_data="cancel_delete_admin")
    kb.adjust(2)
    return kb.as_markup()

