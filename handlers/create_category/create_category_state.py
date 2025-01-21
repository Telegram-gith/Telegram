from aiogram.fsm.state import StatesGroup, State


class CreateCategoryState(StatesGroup):
    category_name = State()
