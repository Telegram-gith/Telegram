from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.translation import _


# Generate category buttons
async def category_kb(categories):
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category.name, callback_data=f"select_category_{category.id}")
    kb.adjust(2)
    return kb.as_markup()


async def catalog_product_kb(products):
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.button(text=product.name, callback_data=f"select_catalog_product_{product.id}")
    kb.adjust(2)
    return kb.as_markup()


# Generate product card buttons
async def product_card_kb(lang, product_id, current_quantity):
    kb = InlineKeyboardBuilder()
    if current_quantity > 0:
        kb.button(text="➖", callback_data=f"decrease_quantity_{product_id}")
        kb.button(text=f"{current_quantity}", callback_data=f"quantity_display_{product_id}")
        kb.button(text="➕", callback_data=f"increase_quantity_{product_id}")
        kb.button(text=_("🛒 Добавить в корзину", lang), callback_data=f"add_basket_{product_id}_{current_quantity}")
        kb.button(text=_("✅ Подтвердить", lang), callback_data=f"confirm_order_{product_id}_{current_quantity}")
        kb.button(text=_("Отменить", lang), callback_data="cancel_order")
        kb.adjust(3, 1)
    else:
        kb.button(text=_("Все продано", lang), callback_data="sold_out")
    return kb.as_markup()


# Generate basket management buttons
async def basket_management_kb(lang, product_id, current_quantity):
    kb = InlineKeyboardBuilder()
    kb.button(text="➖", callback_data=f"basket_decrease_{product_id}")
    kb.button(text=f"{current_quantity}", callback_data=f"basket_quantity_{product_id}")
    kb.button(text="➕", callback_data=f"basket_increase_{product_id}")
    kb.button(text="Remove", callback_data=f"delete_basket_{product_id}")
    kb.button(text=_("Отменить", lang), callback_data="cancel_order")
    kb.adjust(3, 1)
    return kb.as_markup()

