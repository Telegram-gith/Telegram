from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.translation import _


# Inline keyboard for a specific order
def order_specific_kb(lang, product_id, ID):
    kb = InlineKeyboardBuilder()
    kb.button(text=_('🗑️ Удалить', lang), callback_data=f'delete_order_{product_id}_{ID}')
    kb.button(text=_('✅ Подтвердить', lang), callback_data=f'basket_confirm_order_{product_id}_{ID}')
    kb.adjust(2)
    return kb.as_markup()


# Reply keyboard for basket operations
def basket_reply_kb(lang, messages_id):
    kb = ReplyKeyboardBuilder()
    kb.button(text=_('‼️ Очистить корзину', lang))
    kb.button(text=_('❌ Отменить операцию', lang))
    print(messages_id)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
