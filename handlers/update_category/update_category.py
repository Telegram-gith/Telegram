from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from filters.check_admin import CheckAdmin, CheckSuperAdmin
from database.Database import DataBase
from handlers.update_category.update_category_kb import category_inline_kb, cancel_category_kb
from handlers.update_category.update_category_state import UpdateCategoryState
from handlers.start.start_kb import start_kb


update_category_router = Router()


@update_category_router.message(or_f(F.text.lower() == 'отменить', F.text.lower() == 'cancel'))
async def cmd_cancel_message(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = db.get_lang(str(message.from_user.id))
    await state.clear()
    await bot.send_message(message.from_user.id, 'Операция отменена', reply_markup=start_kb(lang))


# Start the edit category process
@update_category_router.message(or_f(F.text.lower() == '/редактировать категорию', F.text.lower() == 'редактировать категорию'), or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def start_edit_category(message: Message, state: FSMContext, bot: Bot):
    await bot.send_message(
        message.from_user.id,
        "Выберите категорию для редактирования: ",
        reply_markup=await category_inline_kb()
    )
    await state.set_state(UpdateCategoryState.select_category)


# Handle category selection
@update_category_router.callback_query(UpdateCategoryState.select_category)
async def handle_category_selection(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split("_")[-1])
    await state.update_data(select_category=category_id)
    await call.message.answer(
        "Введите новое название для категории:",
        reply_markup=await cancel_category_kb()
    )
    await state.set_state(UpdateCategoryState.edit_category_name)
    await call.answer()


# Handle input for category name and perform updates
@update_category_router.message(UpdateCategoryState.edit_category_name)
async def handle_new_category_name(message: Message, state: FSMContext, bot: Bot):
    if message.text.strip():
        db = DataBase()
        data = await state.get_data()
        try:
            await db.update_category(data["select_category"], message.text.strip())
            await bot.send_message(
                message.from_user.id,
                "Название категории успешно обновлено!"
            )
        except Exception as e:
            print(e)
            await bot.send_message(
                message.from_user.id,
                "Не удалось обновить название категории. Пожалуйста, попробуйте снова."
            )
        finally:
            await state.clear()
    else:
        await bot.send_message(message.from_user.id, "Название категории не может быть пустым. Пробовать снова.")


# Handle cancel logic
@update_category_router.callback_query(F.data == "cancel_category")
async def cancel_edit(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = db.get_lang(str(call.from_user.id))
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Операция отменена", reply_markup=start_kb(lang))
    await call.answer()
