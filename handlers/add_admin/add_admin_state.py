from aiogram.fsm.state import StatesGroup, State


class AddAdminState(StatesGroup):
    username = State()
    telegram_id = State()
