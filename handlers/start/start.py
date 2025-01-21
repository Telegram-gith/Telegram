from aiogram import Bot, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.start.start_kb import *
from handlers.start.register_state import *
from database.Database import DataBase
from filters.check_admin import CheckAdmin
from core.translation import _

start_router = Router()


@start_router.message(Command(commands="start"))
async def handle_start(message: Message, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))  # Получаем язык из базы данных
    print(lang)

    try:
        check_admin = CheckAdmin()
        is_admin = await check_admin.__call__(message)  # Проверка прав администратора

        if is_admin:
            await bot.send_message(
                message.from_user.id,
                _("Выберите язык / Choose your language", lang),
                reply_markup=language_selection()
            )
        else:
            user = await db.get_user(str(message.from_user.id))
            print(user)

            if user:
                await bot.send_message(
                    message.from_user.id,
                    _("welcoming", lang),
                    reply_markup=start_kb(lang)
                )
            else:
                await bot.send_message(
                    message.from_user.id,
                    _("Выберите язык / Choose your language", lang),
                    reply_markup=language_selection()
                )
    except Exception as e:
        print(f"Error in handle_start function: {e}")
        await bot.send_message(message.from_user.id, _("Что-то произошло не так. Пожалуйста, повторите позже", lang))


@start_router.callback_query(F.data.startswith('lang_'))
async def handle_language_selection(call: CallbackQuery, bot: Bot):
    lang = call.data.split('_')[-1]
    try:
        db = DataBase()
        check_admin = CheckAdmin()
        is_admin = await check_admin(call)
        print(is_admin)
        await call.message.edit_reply_markup()
        await db.add_language(str(call.from_user.id), lang)
        if is_admin:
            await bot.send_message(
                call.from_user.id,
                _("Приветствуем Админ!", lang),
                reply_markup=start_kb(lang)
            )
        else:
            await call.message.answer(
                _("Язык успешно выбран. Пожалуйста, зарегистрируйтесь.", lang),
                reply_markup=register_kb(lang)
            )
    except Exception as e:
        print(f"Error in handle_language_selection function: {e}")
        await call.answer(_("Что-то произошло не так. Пожалуйста, повторите позже", lang), show_alert=True)


@start_router.callback_query(F.data == 'english')
async def start_register(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.answer(_('📝 Пожалуйста, введите ваше имя', lang))
    await state.set_state(RegisterState.name)
    await call.answer()


@start_router.message(RegisterState.name)
async def username_input(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(message.from_user.id, text=_("📝 Пожалуйста, введите вашу фамилию", lang))
    await state.update_data(name=message.text)
    await state.set_state(RegisterState.surname)


@start_router.message(RegisterState.surname)
async def surname_input(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(message.from_user.id, text=_("📝 Пожалуйста, отправьте ваш номер", lang),
                           reply_markup=phone_button(lang))
    await state.update_data(surname=message.text)
    await state.set_state(RegisterState.phone)


@start_router.message(F.content_type == "contact", StateFilter(RegisterState.phone))
async def phone_input(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    if message.contact and message.contact.phone_number:
        # Update the state data with the provided phone number
        await state.update_data(phone=message.contact.phone_number)
        # Retrieve all state data for user registration
        reg_data = await state.get_data()
        # Add the user to the database
        await db.add_user(
            reg_data.get('name'),
            reg_data.get('surname'),
            reg_data.get('phone'),
            str(message.from_user.id)
        )
        # Send a message confirming the registration
        await bot.send_message(
            chat_id=message.from_user.id,
            text=_('welcoming', lang),
            reply_markup=start_kb(lang)
        )
        # Clear the state after successful registration
        await state.clear()
    else:
        # Ask the user to use the button for sharing their contact
        await bot.send_message(
            chat_id=message.from_user.id,
            text=_("❗ Пожалуйста, отправьте ваш номер", lang)
        )
