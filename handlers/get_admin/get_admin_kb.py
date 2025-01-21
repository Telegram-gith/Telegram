from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase


async def get_admin_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    admins = await db.get_admins()  # Ensure you have a method `get_all_admins` in your database class
    for i, admin in enumerate(sorted(admins, key=lambda a: a.id)):
        kb.button(text=f"{i+1}. {admin.username}", callback_data=f"get_admin_{admin.id}")
    kb.adjust(2)
    return kb.as_markup()


async def return_admin_list_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться к списку администраторов", callback_data="return_admin_list")
    kb.button(text="Вернуться в главное меню", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()
