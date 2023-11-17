from aiogram.types import CallbackQuery
from aiogram import Router, F
from keyboards import kb_admin
from data.logger import logger
from aiogram.fsm.context import FSMContext
from filters.known_user import KnownUser
from filters.is_admin import IsAdmin
from states.states import DelTgAccState
from database import db
router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'tg_accs_del', KnownUser())
async def del_input_phone(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting phone to delete telegram account')
    #await callback.message.delete()
    tg_accs = await db.db_get_all_tg_accounts()
    await callback.message.answer('Пожалуйста, введите номер телефона удаляемого аккаунта: ',
                                  reply_markup=kb_admin.generate_accs_keyboard(tg_accs, 'delete'))
    await state.set_state(DelTgAccState.input_number)


@router.callback_query(F.data.startswith('account_delete'))
async def acc_deleted(callback: CallbackQuery, state: FSMContext):
    acc = callback.data.split('_')[-1]
    await db.db_remove_tg_account(acc)
    logger.info('telegram account deleted from db')
    #await callback.message.delete()
    await callback.message.answer('Аккаунт удален из базы данных')
    await callback.message.answer('Настройки телеграм аккаунтов:', reply_markup=kb_admin.tg_accs_btns())
    await state.clear()
