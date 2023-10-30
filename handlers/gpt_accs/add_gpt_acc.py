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
from database.db_action import db_add_tg_account, db_get_all_tg_accounts, db_add_gpt_account
router = Router()


async def gpt_acc_in_table(phone):
    accounts = await db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


@router.callback_query(F.data == 'gpt_accs_add')
async def input_gpt_acc(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting api key for gpt account')
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите API ключ ChatGPT: ', reply_markup=gpt_back())
    await state.set_state(AddGPTAccState.input_api)


@router.message(AddGPTAccState.input_api)
async def gpt_acc_added(message: Message, state: FSMContext):
    await message.delete()
    api_key = message.text.strip()
    await db_add_gpt_account(api_key)
    await message.answer('API ключ добавлен в базу данных.')
    await message.answer('Настройки ChatGPT аккаунтов:', reply_markup=gpt_accs_btns())

