from aiogram.utils.keyboard import InlineKeyboardBuilder


def language_selection_update():
    kb = InlineKeyboardBuilder()
    kb.button(text="English", callback_data="language_en")
    kb.button(text="Русский", callback_data="language_ru")
    kb.button(text="O'zbek", callback_data="language_uz")
    return kb.as_markup()
