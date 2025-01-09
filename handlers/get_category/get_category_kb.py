from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Category


async def get_category_inline_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    categories = await db.get_table(Category)  # Fetch categories from DB
    for i, category in enumerate(sorted(categories, key=lambda c: c.id)):
        kb.button(text=f"{i+1}. {category.name}", callback_data=f"get_category_{category.id}")
    kb.adjust(2)
    return kb.as_markup()


async def return_category_list_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Вернуться в главное меню", callback_data="return_main")
    kb.button(text="Вернуться к списку категорий", callback_data="back_to_list")
    kb.adjust(1)
    return kb.as_markup()
