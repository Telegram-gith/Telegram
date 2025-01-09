from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from handlers.start.start_kb import start_kb, register_kb
from database.Database import DataBase
from handlers.basket.basket_kb import *
from core.translation import _
from Google_sheets.Google_sheets import add_order_to_queue
from handlers.catalog.catalog import format_price

basket_router = Router()


@basket_router.message(or_f(F.text == '/basket', F.text.contains('🛒 ')))
async def home_basket(message: Message, bot: Bot):
    db = DataBase()
    user_id = str(message.from_user.id)

    # Fetch the user's language preference
    lang = await db.get_lang(user_id)
    basket_text = _('🛒 Корзина', lang)

    # Check if the message text matches the basket command
    if message.text in basket_text or message.text == '/basket':
        # Verify if the user is registered
        user = await db.get_user(user_id)
        if not user:
            await bot.send_message(
                user_id,
                _("Сначала вам нужно зарегистрироваться", lang),
                reply_markup=register_kb(lang)
            )
        else:
            # Fetch and display products in the basket
            products = await db.get_basket(user_id)

            if products:
                for product in products:
                    # Fetch product details
                    item = await db.get_product_one(product.product)
                    formatted_price = format_price(product.product_sum)
                    await bot.send_photo(
                        user_id,
                        photo=item.images,
                        caption=(
                            f"<b>{item.name}</b>\n\n" +
                            _('Описание: ', lang) + f"{item.description}\n" +
                            _('Цена: ', lang) + f"{item.price}" + _(" сум", lang) + '\n' +
                            _('Количество: ', lang) + f"{product.product_quantity}\n" +
                            _('Сумма: ', lang) + f"{formatted_price}"
                        ),
                        reply_markup=order_specific_kb(lang, product_id=product.product, ID=product.id)
                    )

                # Add the options to proceed or clear the basket
                await bot.send_message(
                    user_id,
                    _("Что бы вы хотели сделать дальше?", lang),
                    reply_markup=basket_reply_kb(lang)
                )
            else:
                # Handle the case where the basket is empty
                await bot.send_message(
                    user_id,
                    _('Ваша корзина пуста', lang),
                    reply_markup=start_kb(lang)
                )
    else:
        return


# Delete a specific order
@basket_router.callback_query(F.data.startswith('delete_order_'))
async def delete_order(call: CallbackQuery):
    product_id = int(call.data.split('_')[-2])
    basket_id = int(call.data.split('_')[-1])
    user_id = str(call.from_user.id)
    db = DataBase()
    lang = await db.get_lang(user_id)

    basket_item = await db.get_basket_item(product_id, user_id, basket_id)
    if basket_item:
        # Увеличиваем количество товара на складе
        product = await db.get_product_one(product_id)
        new_quantity = product.quantity + basket_item.product_quantity
        await db.update_product_quantity(product_id, new_quantity)

        # Удаляем заказ из корзины
        await db.delete_basket_one(product_id, user_id, basket_id)
        await call.message.answer(
            _("Заказ на ", lang) + f"{product.name}" + _(" был удален.", lang)
        )
        await call.message.edit_reply_markup(reply_markup=None)
    else:
        await call.message.answer(
            _("Заказ не найден или уже удален.", lang)
        )

    # Проверяем оставшиеся заказы в корзине
    remaining_orders = await db.get_basket(user_id)
    if not remaining_orders:
        await call.message.answer(
            _("Ваша корзина пуста", lang), reply_markup=start_kb(lang)
        )
    else:
        await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()


@basket_router.callback_query(F.data.startswith('basket_confirm_order_'))
async def confirm_order(call: CallbackQuery):
    product_id = int(call.data.split('_')[-2])
    basket_id = int(call.data.split('_')[-1])
    user_id = str(call.from_user.id)
    db = DataBase()
    lang = await db.get_lang(user_id)

    basket_item = await db.get_basket_item(product_id, user_id, basket_id)
    if basket_item:
        # Получаем данные пользователя и товара
        user = await db.get_user(user_id)
        product = await db.get_product_one(product_id)

        # Подтверждаем заказ
        await db.confirm_product(
            basket_item.product_sum,
            product.name,
            basket_item.product_quantity,
            user_id,
            user.username,
            user.usersurname,
            user.userphone,
            status=0
        )

        order_data = await db.prepare_orders_for_sheet()
        await add_order_to_queue(order_data)

        # Удаляем заказ из корзины
        await db.delete_basket_one(product_id, user_id, basket_id)

        # Уведомляем пользователя
        await call.message.answer(
            _("Заказ на ", lang) + f"{product.name}" + _(" был подтвержден.", lang),
            reply_markup=start_kb(lang)
        )
        await call.message.edit_reply_markup(reply_markup=None)

        # Уведомляем администраторов
        admins = await db.get_admins()
        for admin in admins:
            await call.bot.send_message(
                admin.telegram_id,
                _(f"Новый подтвержденный заказ из корзины\n\n", lang) +
                _(f"Пользователь: ", lang) + f"{user.username} {user.usersurname}\n" +
                _(f"Телефон: ", lang) + f"{user.userphone}\n" +
                _(f"Продукт:", lang) + f"{product.name}\n" +
                _(f"Количество: ", lang) + f"{basket_item.product_quantity}\n" +
                _(f"Сумма: ", lang) + f"{basket_item.product_sum}\n" +
                _(f"Статус: В стадии рассмотрения", lang)
            )
        super_admin_id = "6102015555"
        await call.bot.send_message(
            super_admin_id,
            _(f"Получен новый заказ! \n\n", lang) +
            _(f"Пользователь: ", lang) + f"{user.username} {user.usersurname}\n" +
            _(f"Телефон: ", lang) + f"{user.userphone}\n" +
            _(f"Продукт: ", lang) + f"{product.name}\n" +
            _(f"Количество: ", lang) + f"{basket_item.product_quantity}\n" +
            _(f"Сумма: ", lang) + f"{basket_item.product_sum}\n" +
            _(f"Статус: В стадии рассмотрения", lang)
        )

    # Проверяем оставшиеся заказы в корзине
    remaining_orders = await db.get_basket(user_id)
    if not remaining_orders:
        await call.message.answer(
            _("Ваша корзина пуста.", lang), reply_markup=start_kb(lang)
        )
    else:
        await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()


# Delete all orders from the basket
@basket_router.message(F.text.contains("‼️ "))
async def delete_all_orders(message: Message):
    db = DataBase()
    user_id = str(message.from_user.id)
    basket_items = await db.get_basket(user_id)
    lang = await db.get_lang(str(message.from_user.id))
    basket_delete_text = _('‼️ Очистить корзину', lang)

    if message.text not in basket_delete_text:
        return
    else:
        # Restore product quantities
        for item in basket_items:
            product = await db.get_product_one(item.product)
            new_quantity = product.quantity + item.product_quantity
            await db.update_product_quantity(item.product, new_quantity)

        # Clear the basket
        await db.delete_basket_all(user_id)
        await message.answer(_(f"Все заказы были удалены.", lang), reply_markup=start_kb(lang))


# Cancel operation
@basket_router.message(F.text.contains('❌ '))
async def cancel_operation(message: Message):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    basket_cancel_text = _('❌ Отменить операцию', lang)
    if message.text not in basket_cancel_text:
        return
    else:
        await message.answer(_("Операция отменена. Возврат в главное меню.", lang), reply_markup=start_kb(lang))
