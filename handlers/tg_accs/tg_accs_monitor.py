from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import tg_accs_btns, generate_accs_keyboard
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from aiogram.fsm.context import FSMContext
from states.states import AddTgAccState
from data.config_telethon_scheme import AuthTelethon
from database.db_action import db_get_all_tg_accounts, db_remove_tg_account, db_add_tg_monitor_account, db_get_monitor_account
router = Router()


async def acc_in_table(phone):
    accounts = await db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


@router.callback_query(F.data == 'tg_accs_monitor', KnownUser())
async def input_monitor(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    logger.info('awaiting acc to set monitor')
    accounts = await db_get_all_tg_accounts()
    cur_monitor = ''.join(await db_get_monitor_account()) or 'Нет'
    await callback.message.answer(f'Текущий аккаунт для мониторинга: {cur_monitor}\n'
                                  'Выберите аккаунт, который будет мониторить каналы:',
                                  reply_markup=generate_accs_keyboard(accounts, 'monitor'))
    # #await callback.message.delete()


@router.callback_query(F.data.startswith('account_monitor'))
async def set_monitor_acc(callback: CallbackQuery):
    #await callback.message.delete()
    acc = callback.data.split('_')[-1]
    await db_remove_tg_account(acc)
    await db_add_tg_monitor_account(acc)
    await callback.message.answer('Аккаунт для мониторинга установлен.', reply_markup=tg_accs_btns())