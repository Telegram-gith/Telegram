from aiogram.fsm.state import StatesGroup, State


class DeleteOrderState(StatesGroup):
    waiting_for_admin_selection = State()
