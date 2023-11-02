from aiogram.fsm.state import StatesGroup, State


class AddTgAccState(StatesGroup):
    input_number = State()
    input_2fa = State()
    input_code = State()


class DelTgAccState(StatesGroup):
    input_number = State()
    update_db = State()


class AddGroup(StatesGroup):
    input_group = State()


class DelGroup(StatesGroup):
    input_group = State()


class EditPromts(StatesGroup):
    edit_promt = State()

class Triggers(StatesGroup):
    add_trigger = State()
    del_trigger = State()

class AddGPTAccState(StatesGroup):
    input_api = State()