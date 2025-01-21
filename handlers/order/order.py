from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message
from database.Database import DataBase
from core.translation import _
from handlers.start.start_kb import register_kb
from handlers.catalog.catalog import format_price

order_router = Router()


@order_router.message(or_f(F.text.lower() == '/order', F.text.lower() == 'order', F.text.contains('⭐️ ')))
async def order_view(message: Message, bot: Bot):
    db = DataBase()
    user_id = str(message.from_user.id)
    lang = await db.get_lang(user_id)
    order_text = _('⭐️ Заказы', lang)
    # Check if the message text matches the order command
    if message.text in order_text or message.text == '/order':
        # Verify if the user is registered
        user = await db.get_user(user_id)
        if not user:
            await bot.send_message(
                user_id,
                _("Сначала вам нужно зарегистрироваться", lang),
                reply_markup=register_kb(lang)
            )
        else:
            # Fetch and display orders
            orders = await db.get_orders(user_id)
            if orders:
                await bot.send_message(user_id, _('Список заказов: ', lang))
                # Define order status translations
                order_status = {
                    0: _('✅ Заказ подтвержден', lang),
                }
                # Iterate through orders and display details
                for index, order in enumerate(orders, start=1):
                    formatted_price = format_price(order.sum_order)
                    status = order_status.get(order.order_status, _("Неизвестный статус", lang))
                    await bot.send_message(
                        user_id,
                        _(f"Заказ", lang) + f" #{index}:\n" +
                        _("Статус заказа: ", lang) + f"{status}\n" +
                        _("Сумма заказа: ", lang) + f"{formatted_price}" + _(" сум", lang) + '\n' +
                        _("Количество продукта: ", lang) + f"{order.order_quantity}\n"
                    )
            else:
                # Handle case where no orders are found
                await bot.send_message(user_id, _('Заказов не найдено.', lang))
    else:
        return
