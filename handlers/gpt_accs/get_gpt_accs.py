from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import tg_accs_btns, gpt_accs_btns, gpt_back
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import AddGPTAccState
from data.config_telethon_scheme import AuthTelethon
from database.db_action import db_add_tg_account, db_get_all_tg_accounts, db_add_gpt_account, db_get_all_gpt_accounts
from data.chat_gpt import AuthOpenAI
router = Router()


async def gpt_acc_in_table(phone):
    accounts = await db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


@router.callback_query(F.data == 'gpt_accs_info')
async def get_info_gpt_accs(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting info about gpt accs')
    #await callback.message.delete()
    await callback.message.answer('Запрашиваю информацию о API ключах...')
    api_keys = await db_get_all_gpt_accounts()
    keys_status = dict()
    keys_status_list = []
    if api_keys:
        for key in api_keys:
            gpt_acc = AuthOpenAI(key)
            send_req = await gpt_acc.check_work()
            keys_status[key] = send_req
        for key, value in keys_status.items():
            keys_status_list.append(f'Ключ: {key}\nСтатус: {value}')

        keys_status_list = '\n'.join(keys_status_list)
        await callback.message.answer(text=f'API ключи:\n\n{keys_status_list}', reply_markup=gpt_back())
    else:
        await callback.message.answer(text=f'Нет добавленных API ключей.')
        await callback.message.answer(text=f'Настройки телеграм аккаунтов:.', reply_markup=gpt_accs_btns())


