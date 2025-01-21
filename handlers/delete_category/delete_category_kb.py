from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.model import Category


async def get_category_inline_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    categories = await db.get_table(Category)  # Get all categories
    for i, category in enumerate(sorted(categories, key=lambda c: c.id)):
        kb.button(text=f"{category.id}. {category.name}", callback_data=f"delete_category_{category.id}")
    kb.adjust(2)
    return kb.as_markup()


async def delete_category_kb(category_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Удалить", callback_data=f"confirm_delete_{category_id}")
    kb.button(text="Отменить", callback_data="cancel_delete_cat")
    kb.adjust(2)
    return kb.as_markup()
