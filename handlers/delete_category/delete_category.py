from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import or_f
from database.Database import DataBase
from filters.check_admin import CheckAdmin, CheckSuperAdmin

from handlers.delete_category.delete_category_kb import get_category_inline_kb, delete_category_kb

delete_category_router = Router()


# Start delete category process
@delete_category_router.message(or_f(F.text.lower() == "/удалить категорию", F.text.lower() == "удалить категорию"),
                                or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def delete_category_start(message: Message, bot: Bot):
    db = DataBase()
    categories = await db.get_all_categories()
    if categories:
        await bot.send_message(
            message.from_user.id,
            "Выберите категорию для удаления: ",
            reply_markup=await get_category_inline_kb()
        )
    else:
        await message.answer("Нет категорий для удаления")


# Handle the category selection via inline button
@delete_category_router.callback_query(F.data.startswith("delete_category_"))
async def select_category_to_delete(call: CallbackQuery):
    category_id = int(call.data.split("_")[-1])
    await call.message.edit_reply_markup(reply_markup=None)
    # Save category ID in FSM state context to keep track
    await call.message.answer(
        "Теперь вы можете удалить категорию или отменить это действие.",
        reply_markup=await delete_category_kb(category_id)
    )
    await call.answer()


# Confirm delete category
@delete_category_router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_category(call: CallbackQuery):
    category_id = int(call.data.split("_")[-1])
    db = DataBase()
    try:
        await db.delete_category(category_id)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer("Категория успешно удалена!")
    except Exception as e:
        print(f"Error: {e}")
        await call.message.answer("Не удалось удалить категорию. Пожалуйста, попробуйте снова.")
    await call.answer()


# Handle cancel action
@delete_category_router.callback_query(F.data == "cancel_delete_cat")
async def cancel_delete(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Действие отменено.")
    await call.answer()
