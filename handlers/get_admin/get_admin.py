from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from handlers.start.start_kb import start_kb
from database.Database import DataBase
from handlers.get_admin.get_admin_kb import get_admin_kb, return_admin_list_kb
from filters.check_admin import CheckSuperAdmin


get_admin_router = Router()


@get_admin_router.message(or_f(F.text.lower() == '/список админов', F.text.lower() == 'список админов'), CheckSuperAdmin("6102015555"))
async def get_admin_list(message: Message, bot: Bot):
    db = DataBase()
    admins = await db.get_admins()
    if admins:
        await bot.send_message(message.from_user.id, 'Выберите администратора, которого вы хотите видеть:',
                               reply_markup=await get_admin_kb())
    else:
        await message.answer("Администраторы недоступны.")


@get_admin_router.message(or_f(F.text.lower() == '/get_admin', F.text.lower() == 'admin list'))
async def non_super_admin(message: Message, bot: Bot):
    db = DataBase()
    lang = db.get_lang(str(message.from_user.id))
    # If the user is not the super admin, send them back to the main menu
    await bot.send_message(message.from_user.id, "Недопустимая команда", reply_markup=start_kb(lang))


@get_admin_router.callback_query(F.data.startswith("get_admin_"))
async def view_admin_details(call: CallbackQuery):
    db = DataBase()
    admin_id = int(call.data.split("_")[-1])
    admin = await db.get_admin(admin_id)  # Ensure you have a `get_admin` method in the database
    if admin:
        # Send admin details
        await call.message.answer(
            f"Сведения об администраторе: \n\n"
            f"Имя пользователя: {admin.username}\n"
            f"Идентификатор телеграммы: {admin.telegram_id}\n",
            reply_markup=await return_admin_list_kb()
        )
    else:
        await call.message.answer("Администратор не найден.")
    await call.answer()


@get_admin_router.callback_query(F.data == 'return_admin_list')
async def return_to_admin_list(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    db = DataBase()
    admins = await db.get_admins()
    if admins:
        await call.message.answer(
            "Выберите администратора для просмотра подробной информации:",
            reply_markup=await get_admin_kb()
        )
        await call.answer()
    else:
        await call.answer("Администраторы недоступны.")


@get_admin_router.callback_query(F.data('main_menu'))
async def return_to_main_menu(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        f'Добро пожаловать',
        reply_markup=start_kb(lang)
    )
    await call.answer()
