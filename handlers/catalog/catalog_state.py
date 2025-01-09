from aiogram.fsm.state import State, StatesGroup


class CatalogState(StatesGroup):
    selecting_quantity = State()
    confirming_order = State()
