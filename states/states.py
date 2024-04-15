from aiogram.fsm.state import StatesGroup, State


class AddTgAccState(StatesGroup):
    input_number = State()
    input_2fa = State()
    input_code = State()


class DelTgAccState(StatesGroup):
    input_number = State()
    update_db = State()


class AddGroup(StatesGroup):
    input_channel = State()
    input_discussion = State()


class DelGroup(StatesGroup):
    input_group = State()


class EditPromts(StatesGroup):
    edit_promt = State()


class Triggers(StatesGroup):
    add_trigger = State()
    del_trigger = State()


class AddGPTAccState(StatesGroup):
    input_api = State()


class DelGPTState(StatesGroup):
    input_key = State()


class UsersAddState(StatesGroup):
    input_creds = State()


class UsersDelState(StatesGroup):
    input_id = State()


class PromoteUser(StatesGroup):
    input_promote = State()


class TranferAcc(StatesGroup):
    input_acc = State()


class EditAccInfo(StatesGroup):
    change_name = State()
    change_surname = State()
    change_bio = State()
    change_username = State()


class UkassaPayment(StatesGroup):
    input_sum = State()


class AddSubscription(StatesGroup):
    sub_plan = State()


class UserSendPhoto(StatesGroup):
    input_photo = State()


class ChangeDefPromt(StatesGroup):
    add_promt = State()
    del_promt = State()


class AddFewChannels(StatesGroup):
    input_list = State()


class AddAccsArchive(StatesGroup):
    input_archive = State()


class BuyAccs(StatesGroup):
    input_amount = State()
    confirm_amount = State()


class TopAccsShop(StatesGroup):
    input_amount = State()


class CheckChannels(StatesGroup):
    input_list = State()