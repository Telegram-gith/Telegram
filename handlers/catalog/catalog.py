from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.catalog.catalog_kb import category_kb, product_card_kb, catalog_product_kb
from database.Database import DataBase
from handlers.start.start_kb import register_kb, start_kb
from core.translation import _
from Google_sheets.Google_sheets import write_order_to_sheet

catalog_router = Router()


@catalog_router.message(or_f(F.text == '/catalog', F.text.contains('✨ ')))
async def home_catalog(message: Message, bot: Bot):

    db = DataBase()
    user_id = str(message.from_user.id)

    # Fetch the user's language preference
    lang = await db.get_lang(user_id)
    catalog_text = _('✨ Каталог', lang)

    # Check if the message text matches the catalog command
    if message.text in catalog_text or message.text == '/catalog':
        # Verify if the user is registered
        user = await db.get_user(user_id)
        if not user:
            await bot.send_message(
                user_id,
                _("Сначала вам нужно зарегистрироваться", lang),
                reply_markup=register_kb(lang)
            )
        else:
            # Fetch and display categories
            categories = await db.get_all_categories()
            await bot.send_message(
                user_id,
                _("Выберите категорию", lang),
                reply_markup=await category_kb(categories)
            )
    else:
        return


@catalog_router.callback_query(F.data.startswith('select_category_'))
async def category_catalog(call: CallbackQuery):
    """
    Handles the category selection in the catalog.
    """
    category_id = int(call.data.split('_')[-1])
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    products = await db.get_product(category_id)

    if products:
        await call.message.edit_text(
            _("Выберите продукт: ", lang),
            reply_markup=await catalog_product_kb(products)
        )
    else:
        await call.message.edit_text(_('Для этой категории нет никаких товаров', lang))
    await call.answer()


# Category selection
def format_price(price: float) -> str:
    """Форматируем цену с пробелами между разрядами тысяч."""
    return f"{price:,.2f}".replace(",", " ")


@catalog_router.callback_query(F.data.startswith("select_catalog_product_"))
async def product_catalog(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split('_')[-1])
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    product = await db.get_product_one(product_id)

    if product:
        if product.quantity <= 0:
            await call.message.answer_photo(photo=product.images, caption=f'{product.name}')
            await call.message.answer(
                _('Описание: ', lang) + f'{product.description}\n\n' +
                _('Цена: ', lang) + f'{format_price(product.price)}' + _(" сум", lang) + '\n\n' +
                _('Количество: ', lang) + f'{product.quantity}',
                reply_markup=await product_card_kb(lang, product.id, current_quantity=product.quantity)
            )
        else:
            # Инициализация количества в состоянии FSM
            await state.update_data({f"quantity_{product.id}": 1})

            # Форматируем цену
            formatted_price = format_price(product.price)

            # Отправка сообщения с отформатированной ценой
            await call.message.answer_photo(photo=product.images, caption=f'{product.name}')
            await call.message.answer(
                _('Описание: ', lang) + f'{product.description}\n\n' +
                _('Цена: ', lang) + f'{formatted_price}' + _(" сум", lang) + '\n\n' +
                _('Количество: ', lang) + f'{product.quantity}',
                reply_markup=await product_card_kb(lang, product.id, current_quantity=1)
            )
    else:
        await call.message.edit_text(_("Товар не найден.", lang))
    await call.answer()


# Quantity adjustment
@catalog_router.callback_query(F.data.startswith("decrease_quantity_"))
async def decrease_quantity(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    product_id = int(call.data.split("_")[-1])
    state_data = await state.get_data()
    current_quantity = state_data.get(f"quantity_{product_id}", 1) - 1
    if current_quantity <= 0:
        await call.answer(_("Количество не может быть равно нулю", lang), show_alert=True)
        return
    await state.update_data({f"quantity_{product_id}": current_quantity})
    new_markup = await product_card_kb(lang, product_id, current_quantity)
    if call.message.reply_markup != new_markup:  # Проверяем перед обновлением
        await call.message.edit_reply_markup(reply_markup=new_markup)
    # await call.message.edit_reply_markup(reply_markup=await product_card_kb(lang, product_id, current_quantity))
    await call.answer()


@catalog_router.callback_query(F.data.startswith("increase_quantity_"))
async def increase_quantity(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    product_id = int(call.data.split("_")[-1])
    state_data = await state.get_data()
    current_quantity = state_data.get(f"quantity_{product_id}", 1) + 1
    product = await db.get_product_one(product_id)
    if current_quantity > product.quantity:
        await call.answer(_("Недостаточно доступных запасов.", lang), show_alert=True)
        return
    await state.update_data({f"quantity_{product_id}": current_quantity})
    await call.message.edit_reply_markup(reply_markup=await product_card_kb(lang, product_id, current_quantity))
    await call.answer()


# Confirm order
@catalog_router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    try:
        product_id, quantity = map(int, call.data.split("_")[2:])
        product = await db.get_product_one(product_id)
        user = await db.get_user(str(call.from_user.id))

        if product.quantity < quantity:
            await call.answer(_("Недостаточно доступных запасов.", lang), show_alert=True)
            return

        await db.update_product_quantity(product_id, product.quantity - quantity)
        await db.confirm_product(
            product.price * quantity, product.name, quantity,
            str(call.from_user.id), user.username, user.usersurname, user.userphone, 0
        )

        order_data = await db.prepare_orders_for_sheet()
        await write_order_to_sheet(order_data)

        admins = await db.get_admins()
        print(admins)
        super_admin_id = "6102015555"  # Telegram ID супер-администратора

        for admin in admins:
            await call.bot.send_message(
                admin.telegram_id,
                _(f"Получен новый заказ! \n\n", lang) +
                _(f"Пользователь: ", lang) + f"{user.username} {user.usersurname}\n" +
                _(f"Телефон: ", lang) + f"{user.userphone}\n" +
                _(f"Продукт: ", lang) + f"{product.name}\n" +
                _(f"Количество: ", lang) + f"{quantity}\n" +
                _(f"Сумма: ", lang) + f"{product.price * quantity}\n" +
                _(f"Статус: В стадии рассмотрения", lang)
            )

        # Уведомление супер-администратора
        await call.bot.send_message(
            super_admin_id,
            _(f"Получен новый заказ! \n\n", lang) +
            _(f"Пользователь: ", lang) + f"{user.username} {user.usersurname}\n" +
            _(f"Телефон: ", lang) + f"{user.userphone}\n" +
            _(f"Продукт: ", lang) + f"{product.name}\n" +
            _(f"Количество: ", lang) + f"{quantity}\n" +
            _(f"Сумма: ", lang) + f"{product.price * quantity}\n" +
            _(f"Статус: В стадии рассмотрения", lang)
        )
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(_(f"Заказ подтвержден для ", lang) + f"{product.name}")
        await call.answer()
    except Exception as e:
        print(f"Error in confirm_order: {e}")
        await call.answer(_("При обработке вашего заказа произошла ошибка. Пожалуйста, попробуйте снова.", lang),
                          show_alert=True)


# Add to basket
@catalog_router.callback_query(F.data.startswith("add_basket_"))
async def add_basket(call: CallbackQuery):
    product_id, quantity = map(int, call.data.split("_")[2:])
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    product = await db.get_product_one(product_id)
    if product.quantity < quantity:
        await call.answer(_("Недостаточно доступных запасов.", lang), show_alert=True)
        return
    # Update the product quantity and add to basket
    await db.update_product_quantity(product_id, product.quantity - quantity)
    await db.add_basket(str(call.from_user.id), product.id, quantity, float(product.price * quantity))
    # Notify user about the added product
    await call.message.answer(_(f'Продукт ', lang) + f'{product.name}' + _(' добавлено в вашу корзину.', lang))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()


# Cancel operation
@catalog_router.callback_query(F.data == "cancel_order")
async def cancel_order(call: CallbackQuery):
    db = DataBase()
    categories = await db.get_all_categories()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(_("Операция отменена", lang), reply_markup=await category_kb(categories))
    await call.answer()


@catalog_router.callback_query(F.data == "sold_out")
async def sold_out(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.answer(_('sold out', lang))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
