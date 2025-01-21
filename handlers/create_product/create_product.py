from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.Database import DataBase
from filters.check_admin import CheckAdmin, CheckSuperAdmin
from handlers.create_product.create_product_kb import cancel_kb, category_kb
from handlers.create_product.create_product_state import CreateState
from core.translation import _
from handlers.create_category.create_category import create_category

create_route = Router()


@create_route.message(or_f(F.text.lower() == 'отменить', F.text.lower() == 'cancel'))
async def cmd_cancel_message(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await state.clear()
    await bot.send_message(message.from_user.id, _('Операция отменена', lang))


@create_route.callback_query(F.data == 'cancel')
async def cmd_cancel_inline(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    lang = await db.get_lang(str(call.from_user.id))
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)  # Remove the inline keyboard
    await call.message.answer(_('Операция отменена', lang))
    await call.answer()  # Acknowledge the callback


@create_route.message(or_f(F.text.lower() == '/добавить продукт', F.text.lower() == 'добавить продукт'),
                      or_f(CheckAdmin(), CheckSuperAdmin("6102015555")))
async def create_product(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    categories = await db.get_all_categories()
    if categories:
        await bot.send_message(message.from_user.id, 'Выберите категорию: ', reply_markup=await category_kb())
        await state.set_state(CreateState.category_product)
    else:
        # Сообщение пользователю о необходимости создать категорию
        await bot.send_message(message.from_user.id,
                               "Категории не найдены. Переход к созданию новой категории...",
                               reply_markup=None)
        await create_category(message, state, bot)


@create_route.callback_query(CreateState.category_product)
async def select_category(call: CallbackQuery, state: FSMContext):
    db = DataBase()
    category_name = call.data.split('_')[2]
    category_id = call.data.split('_')[-1]
    lang = await db.get_lang(str(call.from_user.id))
    await call.message.answer(f'Отлично, вы выбрали категорию {category_name}\n\n'
                              f'Введите название продукта: ', reply_markup=await cancel_kb(lang))
    await state.update_data(category_product=int(category_id))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    await state.set_state(CreateState.name_product)


@create_route.message(CreateState.name_product)
async def product_name(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(message.from_user.id, 'Я сохранил имя, теперь пришлите изображение',
                           reply_markup=await cancel_kb(lang))
    await state.update_data(name_product=message.text)
    await state.set_state(CreateState.img_product)


@create_route.message(CreateState.img_product)
async def input_product_img(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    if message.photo is not None:
        await bot.send_message(message.from_user.id, 'Изображение сохранено \n\n' +
                                                     "Введите описание", reply_markup=await cancel_kb(lang))
        await state.update_data(img_product=message.photo[-1].file_id)
        await state.set_state(CreateState.description_product)
    else:
        await bot.send_message(message.from_user.id, f'Я жду фото')


@create_route.message(CreateState.description_product)
async def input_product_description(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    await bot.send_message(message.from_user.id, 'Описание сохранено \n\n'
                                                 'Введите количество продукта', reply_markup=await cancel_kb(lang))
    await state.update_data(description_product=message.text)
    await state.set_state(CreateState.product_quantity)  # Set the correct state for quantity input


@create_route.message(CreateState.product_quantity)
async def input_product_quantity(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    lang = await db.get_lang(str(message.from_user.id))
    if message.text.isdigit():
        await bot.send_message(message.from_user.id, 'Количество продукта сохранено \n\n'
                                                     'Введите цену товара', reply_markup=await cancel_kb(lang))
        await state.update_data(product_quantity=int(message.text))  # Store the quantity as an integer
        await state.set_state(CreateState.price_product)  # Move to price input state
    else:
        await bot.send_message(message.from_user.id, "Я жду целого числа.")


@create_route.message(CreateState.price_product)
async def input_product_price(message: Message, state: FSMContext, bot: Bot):
    # Проверка, что введенная цена - это число с плавающей точкой
    try:
        price = float(message.text)  # Преобразование текста в float
        await state.update_data(price_product=price)  # Обновление состояния с ценой как float
        product = await state.get_data()
        status = 0  # Пример статуса по умолчанию

        # Добавление продукта в базу данных
        try:
            db = DataBase()
            # Добавление продукта в базу данных с использованием состояния
            await db.add_product(
                product['name_product'],
                product['category_product'],
                product['img_product'],
                product['description_product'],
                product['product_quantity'],  # Получение количества продукта
                product['price_product'],  # Использование float для цены
                status,
            )
            await bot.send_message(message.from_user.id, 'Отлично, продукт сохранено', reply_markup=None)
        except Exception as e:
            print(f"Error while adding product: {e}")
            await bot.send_message(message.from_user.id,
                                   'К сожалению, что-то пошло не так, пожалуйста, повторите попытку')
        finally:
            await state.clear()
    except ValueError:  # Если не удалось преобразовать в число с плавающей точкой
        await bot.send_message(message.from_user.id, "Я жду действительную цену (число с плавающей точкой).")
