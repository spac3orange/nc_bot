from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import tg_accs_btns, tg_back, generate_accs_keyboard
from data.logger import logger
from aiogram.fsm.context import FSMContext
from states.states import DelTgAccState
from database.db_action import db_remove_tg_account, db_get_all_tg_accounts
router = Router()


@router.callback_query(F.data == 'tg_accs_del')
async def del_input_phone(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting phone to delete telegram account')
    #await callback.message.delete()
    tg_accs = await db_get_all_tg_accounts()
    await callback.message.answer('Пожалуйста, введите номер телефона удаляемого аккаунта: ',
                                  reply_markup=generate_accs_keyboard(tg_accs, 'delete'))
    await state.set_state(DelTgAccState.input_number)


@router.callback_query(F.data.startswith('account_delete'))
async def acc_deleted(callback: CallbackQuery, state: FSMContext):
    acc = callback.data.split('_')[-1]
    await db_remove_tg_account(acc)
    logger.info('telegram account deleted from db')
    #await callback.message.delete()
    await callback.message.answer('Аккаунт удален из базы данных')
    await callback.message.answer('Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())
    await state.clear()
