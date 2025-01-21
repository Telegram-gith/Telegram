from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.translation import _


def register_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=_("Регистрируйтесь", lang), callback_data="english")
    return kb.as_markup()


def phone_button(lang):
    kb = ReplyKeyboardBuilder()
    kb.button(text=_("📱 Номер телефона", lang), request_contact=True)
    return kb.as_markup(resize_keyboard=True)


def start_kb(lang):
    kb = ReplyKeyboardBuilder()
    kb.button(text=_('✨ Каталог', lang))
    kb.button(text=_('⭐️ Заказы', lang))
    kb.button(text=_('🛒 Корзина', lang))
    return kb.as_markup(resize_keyboard=True)


def language_selection():
    kb = InlineKeyboardBuilder()
    kb.button(text="English", callback_data="lang_en")
    kb.button(text="Русский", callback_data="lang_ru")
    kb.button(text="O'zbek", callback_data="lang_uz")
    return kb.as_markup()
