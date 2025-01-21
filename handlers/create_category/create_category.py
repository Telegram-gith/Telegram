from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.Database import DataBase
from filters.check_admin import CheckAdmin, CheckSuperAdmin
from handlers.create_category.create_category_kb import cancel_kb
from handlers.create_category.create_category_state import CreateCategoryState
from core.translation import _


create_category_router = Router()


@create_category_router.message(or_f(F.text.lower() == 'отменить', F.text.lower() == 'cancel'))
async def category_cancel_message(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await state.clear()
    await bot.send_message(message.from_user.id, _("Операция отменена", lang))


@create_category_router.callback_query(F.data == 'cancel_cat')
async def category_cancel_inline(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)  # Remove the inline keyboard
    await call.message.answer(_('Операция отменена', lang))
    await call.answer()  # Acknowledge the callback


@create_category_router.message(or_f(F.text.lower() == "/добавить категорию", F.text.lower() == "добавить категорию"),
                                or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def create_category(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(str(message.from_user.id),
                           "Пожалуйста, введите название категории, которую вы хотите создать: ",
                           reply_markup=await cancel_kb(lang))
    await state.set_state(CreateCategoryState.category_name)


@create_category_router.message(CreateCategoryState.category_name)
async def input_category_name(message: Message, state: FSMContext, bot: Bot):
    category_name = message.text.strip()
    if category_name:
        # Save to database
        db = DataBase()
        try:
            await db.add_category(category_name)
            await bot.send_message(str(message.from_user.id), f"Категория {category_name} успешно создана!",
                                   reply_markup=None)
        except Exception as e:
            print(e)
            await bot.send_message(message.from_user.id, "Не удалось создать категорию. Пожалуйста, повторите попытку позже.",
                                   reply_markup=None)
        finally:
            await state.clear()
    else:
        await bot.send_message(message.from_user.id, "Имя не может быть пустым. Пожалуйста, попробуйте снова.")
