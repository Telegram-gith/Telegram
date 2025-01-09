from aiogram.fsm.state import StatesGroup, State


class UpdateState(StatesGroup):
    category_product = State()  # Step to update the category of the product
    name_product = State()  # Step to update the name of the product
    img_product = State()  # Step to update the product image
    description_product = State()  # Step to update the product description
    product_quantity = State()  # Step to update the quantity of the product
    price_product = State()  # Step to update the product price
