from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from handlers.update_language.update_language_kb import language_selection_update
from database.Database import DataBase
from handlers.start.start_kb import register_kb, start_kb
from core.translation import _


language_router = Router()


@language_router.message(or_f(F.text == '/language', F.text == 'language'))
async def language_change(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, "Выберите язык / Choose your language",
                           reply_markup=language_selection_update())


@language_router.callback_query(F.data.startswith('language_'))
async def language_selection(call: CallbackQuery, bot: Bot):
    db = DataBase()
    await call.message.edit_reply_markup()
    lang = call.data.split('_')[-1]
    user = await db.get_user(str(call.from_user.id))
    admin = await db.get_admin_by_id(str(call.from_user.id))

    if user or admin:
        await db.update_language(str(call.from_user.id), call.data.split('_')[-1])  # Обновляем язык
        await bot.send_message(
            call.from_user.id,
            _("Язык был изменен", lang),  # Подтверждение изменения языка
            reply_markup=start_kb(lang)
        )
    else:
        await db.add_language(str(call.from_user.id), lang)  # Если пользователь новый
        await call.message.answer(_("Регистрируйтесь", lang), reply_markup=register_kb(lang))
