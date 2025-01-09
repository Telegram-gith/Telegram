from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.translation import _


async def cancel_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=_('Отменить', lang), callback_data=f'cancel_cat')
    kb.adjust(1)
    return kb.as_markup()
