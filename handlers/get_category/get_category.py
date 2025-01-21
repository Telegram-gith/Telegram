from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import or_f
from database.Database import DataBase
from filters.check_admin import CheckAdmin, CheckSuperAdmin
from handlers.start.start_kb import start_kb
from handlers.get_category.get_category_kb import return_category_list_kb, get_category_inline_kb


get_category_router = Router()


# Handle the /get_category command
@get_category_router.message(or_f(F.text.lower() == '/список категорий', F.text.lower() == 'список категорий'), or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def get_category_list(message: Message, bot: Bot):
    # Send list of all categories as inline buttons
    await bot.send_message(
        message.from_user.id,
        "Вот эти категории: ",
        reply_markup=await get_category_inline_kb()
    )


# Handle category selection via inline button click
@get_category_router.callback_query(F.data.startswith("get_category_"))
async def handle_category_selection(call: CallbackQuery):
    category_id = int(call.data.split("_")[-1])
    db = DataBase()
    category = await db.get_category_by_id(category_id)  # Fetch category details
    if category:
        # Send detailed information about the category
        await call.message.answer(
            f"Информация о категории: \n"
            f"Название: {category.name}\n"
            f"ID: {category.id}",
            reply_markup=await return_category_list_kb()
        )
    else:
        await call.message.answer("Категория не найдена.")
    await call.answer()


# Handle the return to main menu
@get_category_router.callback_query(F.data == "return_main")
async def return_to_main(call: CallbackQuery):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Вернулись в главное меню.", reply_markup=start_kb(lang))
    await call.answer()


# Handle the back to the category list
@get_category_router.callback_query(F.data == "back_to_list")
async def back_to_category_list(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=await get_category_inline_kb())
    await call.answer()
