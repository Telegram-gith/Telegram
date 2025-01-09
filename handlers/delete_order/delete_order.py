from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from handlers.start.start_kb import start_kb
from database.Database import DataBase
from filters.check_admin import CheckAdmin
from handlers.delete_order.delete_order_kb import delete_product_kb
from handlers.delete_order.delete_order_state import DeleteOrderState
from aiogram.fsm.context import FSMContext
from core.translation import _


delete_order_router = Router()


# Step 1: Admin selects a user by typing username
@delete_order_router.message(or_f(F.text == '/delete_order', F.text.lower() == 'delete order'), CheckAdmin())
async def delete_order_user_select(message: Message, state: FSMContext):
    await message.answer("Please type the username of the user whose orders you want to delete.")
    await message.answer("You can type part of the username to search for users.")
    await state.set_state(DeleteOrderState.waiting_for_admin_selection)


# Step 2: Handle the user search and show results as inline buttons
@delete_order_router.message(DeleteOrderState.waiting_for_admin_selection)
async def search_users_for_deletion(message: Message, bot: Bot):
    db = DataBase()
    search_term = message.text.strip().lower()
    users = await db.search_users_by_username(search_term)

    if users:
        kb = InlineKeyboardMarkup(inline_keyboard=[])
        for user in users:
            kb.inline_keyboard.append(
                [InlineKeyboardButton(text=user.username, callback_data=f"user_select_{user.telegram_id}")])
        await message.answer("Please select a user from the list:", reply_markup=kb)
    else:
        await bot.send_message(message.from_user.id, "")


# Step 3: Once a user is selected, show their orders
@delete_order_router.callback_query(F.data.startswith("user_select_"))
async def show_user_orders(call: CallbackQuery):
    user_id = call.data.split("_")[-1]
    db = DataBase()
    lang = db.get_lang(str(call.from_user.id))
    orders = await db.get_user_orders(user_id)
    order_status = {
        0: 'Order confirmed'
    }

    if orders:
        for index, order in enumerate(orders, start=1):  # Add an enumerator for order counter
            status = order_status.get(order.order_status, "Unknown status")
            await call.message.answer(_(f"Заказ", lang) + f" #{index}:\n" +
                                      _("Статус заказа: ", lang) + f"{status}\n" +
                                      _("Сумма заказа: ", lang) + f"{order.sum_order}\n" +
                                      _("Количество продукта: ", lang) + f"{order.order_quantity}\n",
                                      reply_markup=await delete_product_kb(order_id=order.id))
    else:
        await call.message.answer("This user has no orders to delete.")

    await call.answer()


# Step 4: Handle the deletion of the order
@delete_order_router.callback_query(F.data.startswith("order_delete_"))
async def delete_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[-1])
    db = DataBase()

    try:
        # Delete the order from the database
        await db.delete_order(order_id)
        await call.message.answer(f"Order has been deleted successfully!")
    except Exception as e:
        print(f"Error: {e}")
        await call.message.answer("Failed to delete the order. Please try again.")

    await call.answer()


# Step 5: Handle the cancellation of the operation
@delete_order_router.callback_query(F.data == "cancel_delete_order")
async def cancel_delete_order(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Operation canceled.", reply_markup=start_kb(lang))
    await call.answer()
