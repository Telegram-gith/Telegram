from aiogram.utils.keyboard import InlineKeyboardBuilder


async def delete_product_kb(order_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Delete", callback_data=f"order_delete_{order_id}")
    kb.button(text="Cancel", callback_data="cancel_delete_order")
    kb.adjust(2)
    return kb.as_markup()