from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import or_f
from database.Database import DataBase
from filters.check_admin import CheckSuperAdmin
from handlers.delete_admin.delete_admin_kb import callback_admin_kb, delete_admin_kb
from handlers.start.start_kb import start_kb


delete_admin_router = Router()


@delete_admin_router.message(or_f(F.text.lower() == '/удалить админа', F.text.lower() == 'удалить админа'),
                             CheckSuperAdmin("6102015555"))
async def delete_admin_list(message: Message, bot: Bot):
    db = DataBase()
    admins = await db.get_admins()
    if admins:
        await bot.send_message(message.from_user.id, 'Выберите администратора, которого вы хотите удалить: ',
                               reply_markup=await callback_admin_kb())
    else:
        await message.answer("Администраторы не доступны для удаления.")


@delete_admin_router.message(or_f(F.text.lower() == '/delete_admin', F.text.lower() == 'delete admin'))
async def non_super_admin(message: Message, bot: Bot):
    db = DataBase()
    lang = db.get_lang(str(message.from_user.id))
    # If the user is not the super admin, send them back to the main menu
    await bot.send_message(message.from_user.id, "Invalid command", reply_markup=start_kb(lang))


@delete_admin_router.callback_query(F.data.startswith('delete_admin_'))
async def select_admin(call: CallbackQuery):
    db = DataBase()
    admin_id = int(call.data.split("_")[-1])
    admin = await db.get_admin(admin_id)
    if admin:
        await call.message.answer(
            f"Информация об администраторе: \n\n"
            f"Имя пользователя: {admin.username}\n"
            f"Идентификатор телеграммы: {admin.telegram_id}\n",
            reply_markup=await delete_admin_kb(admin_id),
        )
    else:
        await call.message.answer("Администратор не найден.")
    await call.answer()


@delete_admin_router.callback_query(F.data.startswith("delete_ad_"))
async def callback_delete_admin(call: CallbackQuery):
    db = DataBase()
    admin_id = int(call.data.split("_")[-1])
    try:
        await db.delete_admin(admin_id)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer("Администратор успешно удален!")
    except:
        await call.message.answer("Не удалось удалить администратора. Пожалуйста, попробуйте снова.")
    await call.answer()


@delete_admin_router.callback_query(F.data.startswith("cancel_delete_admin"))
async def admin_delete_cancel(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Операция отменена.", reply_markup=start_kb(lang))
    await call.answer()
