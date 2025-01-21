from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.Database import DataBase
from filters.check_admin import CheckSuperAdmin
from handlers.add_admin.add_admin_state import AddAdminState
from handlers.add_admin.add_admin_kb import cancel_kb
from handlers.start.start_kb import start_kb
from core.translation import _

add_admin_router = Router()


@add_admin_router.message(or_f(F.text.lower() == 'отменить', F.text.lower() == 'cancel'))
async def add_admin_cancel_message(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await state.clear()
    await bot.send_message(message.from_user.id, _('Операция отменена', lang))


@add_admin_router.callback_query(F.data == 'cancel_add_admin')
async def add_admin_cancel_inline(call: CallbackQuery, state: FSMContext):
    await state.clear()
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)  # Remove the inline keyboard
    await call.message.answer(_('Операция отменена', lang), reply_markup=start_kb(lang))
    await call.answer()  # Acknowledge the callback


@add_admin_router.message(or_f(F.text.lower() == '/добавить админа', F.text.lower() == 'добавить админа'),
                          CheckSuperAdmin("6102015555"))
async def add_admin(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(message.from_user.id, _('Пожалуйста, введите имя админа', lang),
                           reply_markup=await cancel_kb(lang))
    await state.set_state(AddAdminState.username)


@add_admin_router.message(F.text.in_(['/add_admin', 'add admin']))
async def non_super_admin(message: Message, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    # If the user is not the super admin, send them back to the main menu
    await bot.send_message(message.from_user.id, _("Недействительная команда", lang), reply_markup=start_kb(lang))


@add_admin_router.message(AddAdminState.username)
async def input_admin_name(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(message.from_user.id, _('Пожалуйста, введите телеграмм идентификатор администратора', lang),
                           reply_markup=await cancel_kb(lang))
    await state.update_data(username=message.text.strip())
    await state.set_state(AddAdminState.telegram_id)


@add_admin_router.message(AddAdminState.telegram_id)
async def input_admin_telegram_id(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    admin_telegram_id = message.text.strip()
    if admin_telegram_id:
        # Save to database
        await state.update_data(telegram_id=admin_telegram_id)
        admin = await state.get_data()
        try:
            db = DataBase()
            await db.add_admin(admin['username'], admin['telegram_id'])
            await bot.send_message(message.from_user.id,
                                   _("Администратор успешно создан!", lang),
                                   reply_markup=None)
        except Exception as e:
            print(e)
            await bot.send_message(message.from_user.id,
                                   _("Не удалось создать администратора. Пожалуйста, повторите попытку позже.", lang),
                                   reply_markup=None)
        finally:
            await state.clear()
    else:
        await bot.send_message(message.from_user.id, _("Введите действительный идентификатор telegram", lang))
