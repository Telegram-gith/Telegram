from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f

from database.Database import DataBase
from filters.check_admin import CheckSuperAdmin
from handlers.update_admin.update_admin_kb import admin_inline_kb, cancel_admin_kb
from handlers.update_admin.update_admin_state import UpdateAdminState
from handlers.start.start_kb import start_kb

update_admin_router = Router()


@update_admin_router.message(or_f(F.text.lower() == 'отменить', F.text.lower() == 'cancel'))
async def update_admin_cancel_message(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = db.get_lang(str(message.from_user.id))
    await state.clear()
    await bot.send_message(message.from_user.id, 'Операция отменена', reply_markup=start_kb(lang))


@update_admin_router.callback_query(F.data == 'cancel_update_admin')
async def update_admin_cancel_inline(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = db.get_lang(str(call.from_user.id))
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)  # Remove the inline keyboard
    await call.message.answer('Операция отменена', reply_markup=start_kb(lang))
    await call.answer()  # Acknowledge the callback


@update_admin_router.message(or_f(F.text.lower() == '/редактировать админа', F.text.lower() == 'редактировать админа'),
                             CheckSuperAdmin("6102015555"))
async def update_admin_start(message: Message, bot: Bot):
    db = DataBase()
    admins = await db.get_admins()
    if admins:
        await bot.send_message(
            message.from_user.id,
            "Выберите администратора для обновления: ",
            reply_markup=await admin_inline_kb()
        )
    else:
        await bot.send_message(message.from_user.id, "Администраторы не доступны для обновления.")


@update_admin_router.message(or_f(F.text.lower() == '/update_admin', F.text.lower() == 'edit admin'))
async def non_super_admin(message: Message, bot: Bot):
    db = DataBase()
    lang = db.get_lang(str(message.from_user.id))
    # If the user is not the super admin, send them back to the main menu
    await bot.send_message(message.from_user.id, "Недопустимая команда", reply_markup=start_kb(lang))


@update_admin_router.callback_query(F.data.startswith("select_"))
async def admin_selected(call: CallbackQuery, state: FSMContext):
    admin_id = int(call.data.split("_")[-1])
    db = DataBase()
    admin = await db.get_admin(admin_id)
    if admin:
        await state.update_data(admin_id=admin.id, current_data={
            "username": admin.username,
            "telegram_id": admin.telegram_id
        })
        await call.message.answer(f"Обновление администратора: {admin.username}\n"
                                  f"Отправьте новое имя пользователя (или пустое, чтобы пропустить).:",
                                  reply_markup=await cancel_admin_kb())
        await state.set_state(UpdateAdminState.username)
    else:
        await call.message.answer("Администратор не найден.")
    await call.answer()


@update_admin_router.message(UpdateAdminState.username)
async def update_username(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text.strip():  # If not empty
        data["current_data"]["username"] = message.text.strip()
    await state.update_data(current_data=data["current_data"])
    await bot.send_message(message.from_user.id,
                           "Введите новый идентификатор Telegram (или пустой, чтобы пропустить).: ",
                           reply_markup=await cancel_admin_kb())
    await state.set_state(UpdateAdminState.telegram_id)


@update_admin_router.message(UpdateAdminState.telegram_id)
async def update_telegram_id(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text.strip().isdigit():
        data["current_data"]["telegram_id"] = message.text.strip()

    await state.update_data(current_data=data["current_data"])
    await finalize_admin_update(message, state, bot)


async def finalize_admin_update(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    db = DataBase()
    try:
        await db.update_admin(
            data["admin_id"],
            username=data["current_data"]["username"],
            telegram_id=data["current_data"]["telegram_id"]
        )
        await bot.send_message(message.from_user.id, "Администратор успешно обновлен!")
    except Exception as e:
        print(f"Error while updating admin: {e}")
        await bot.send_message(message.from_user.id, "Произошла ошибка при обновлении администратора.")
    finally:
        await state.clear()
