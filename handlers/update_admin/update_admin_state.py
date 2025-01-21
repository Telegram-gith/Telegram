from aiogram.fsm.state import State, StatesGroup


class UpdateAdminState(StatesGroup):
    select_admin = State()
    username = State()
    telegram_id = State()
