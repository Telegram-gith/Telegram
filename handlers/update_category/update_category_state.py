from aiogram.fsm.state import StatesGroup, State


class UpdateCategoryState(StatesGroup):
    select_category = State()  # Select category to edit
    edit_category_name = State()  # Input new name
