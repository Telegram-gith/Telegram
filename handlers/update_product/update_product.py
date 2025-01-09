from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f

from database.Database import DataBase
from filters.check_admin import CheckAdmin, CheckSuperAdmin
from handlers.update_product.update_product_state import UpdateState
from handlers.update_product.update_product_kb import product_inline_kb, category_inline_kb, cancel_kb
from handlers.start.start_kb import start_kb


update_route = Router()


@update_route.message(or_f(F.text.lower() == 'отменить', F.text.lower() == 'cancel'))
async def cmd_cancel_message(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = db.get_lang(str(message.from_user.id))
    await state.clear()
    await bot.send_message(message.from_user.id, 'Операция отменена', reply_markup=start_kb(lang))


@update_route.callback_query(F.data == 'cancel')
async def cmd_cancel_inline(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = db.get_lang(str(call.from_user.id))
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)  # Remove the inline keyboard
    await call.message.answer('Операция отменена', reply_markup=start_kb(lang))
    await call.answer()  # Acknowledge the callback


# Start update process
@update_route.message(or_f(F.text.lower() == '/редактировать продукт', F.text.lower() == 'редактировать продукт'),
                      or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def update_product_start(message: Message, bot: Bot):
    db = DataBase()
    products = await db.get_all_products()
    if products:
        await bot.send_message(
            message.from_user.id,
            "Выберите продукт для обновления: ",
            reply_markup=await product_inline_kb()
        )
    else:
        await bot.send_message(message.from_user.id, "Нет продуктов, доступных для обновления.")


# Handle product selection via inline buttons
@update_route.callback_query(F.data.startswith("update_product_"))
async def product_selected(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[-1])
    db = DataBase()
    product = await db.get_product_one(product_id)
    if product:
        await state.update_data(product_id=product.id, current_data={
            "name": product.name,
            "category_id": product.category_id,
            "img": product.images,
            "description": product.description,
            "quantity": product.quantity,
            "price": product.price,
        })
        await call.message.answer(f"Обновление продукта: {product.name}\n"
                                  f"Отправьте новое имя (или пустое, чтобы пропустить):",
                                  reply_markup=await cancel_kb())
        await state.set_state(UpdateState.name_product)
    else:
        await call.message.answer("Товар не найден.")
    await call.answer()


# Update product name
@update_route.message(UpdateState.name_product)
async def update_name(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text.strip():  # If not empty
        data["current_data"]["name"] = message.text.strip()
    await state.update_data(current_data=data["current_data"])
    await bot.send_message(message.from_user.id, "Выберите категорию: ",
                           reply_markup=await category_inline_kb())
    await state.set_state(UpdateState.category_product)


@update_route.callback_query(UpdateState.category_product)
async def update_category(call: CallbackQuery, state: FSMContext, bot: Bot):
    category_id = call.data.split("_")[-1]
    data = await state.get_data()
    data["current_data"]["category_id"] = int(category_id)
    await state.update_data(current_data=data["current_data"])
    await bot.send_message(call.from_user.id, "Загрузить изображение (или пустое, чтобы пропустить): ",
                           reply_markup=await cancel_kb())
    await state.set_state(UpdateState.img_product)


# Update product image
@update_route.message(UpdateState.img_product)
async def update_image(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.photo:
        data["current_data"]["img"] = message.photo[-1].file_id
    await state.update_data(current_data=data["current_data"])
    await bot.send_message(message.from_user.id, "Введите новое описание (или пустое, чтобы пропустить).: ",
                           reply_markup=await cancel_kb())
    await state.set_state(UpdateState.description_product)


# Update product description
@update_route.message(UpdateState.description_product)
async def update_description(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text.strip():
        data["current_data"]["description"] = message.text.strip()
    await state.update_data(current_data=data["current_data"])
    await bot.send_message(message.from_user.id, "Введите новое количество (или пустое, чтобы пропустить): ",
                           reply_markup=await cancel_kb())
    await state.set_state(UpdateState.product_quantity)


# Update product quantity
@update_route.message(UpdateState.product_quantity)
async def update_quantity(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text.strip().isdigit():
        data["current_data"]["quantity"] = int(message.text.strip())
    await state.update_data(current_data=data["current_data"])
    await bot.send_message(message.from_user.id, "Введите новую цену (или пустое поле для пропуска).:",
                           reply_markup=await cancel_kb())
    await state.set_state(UpdateState.price_product)


# Update product price
@update_route.message(UpdateState.price_product)
async def update_price(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    # Validate price input: allow float with dot or comma as separator
    try:
        price_input = message.text.strip()  # Replace comma with dot for correct float parsing
        data["current_data"]["price"] = float(price_input)
    except ValueError:
        await bot.send_message(message.from_user.id,
                               "Пожалуйста, введите действительное числовое значение с точкой для дробной части.")
        return  # Exit if invalid input

    await state.update_data(current_data=data["current_data"])
    status = 0

    # Finalize product update
    db = DataBase()
    try:
        await db.update_product(
            data["product_id"],
            data["current_data"]["name"],
            data["current_data"]["category_id"],
            data["current_data"]["img"],
            data["current_data"]["description"],
            data["current_data"]["quantity"],
            data["current_data"]["price"],
            status
        )
        await bot.send_message(message.from_user.id, "Продукт успешно обновлен!")
    except Exception as e:
        print(f"Error while updating product: {e}")
        await bot.send_message(message.from_user.id, "При обновлении продукта произошла ошибка.")
    finally:
        await state.clear()
