from aiogram.types import CallbackQuery
from data.logger import logger
from aiogram import Router, F
from keyboards import kb_admin
from filters.known_user import KnownUser
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from database import db
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def acc_in_table(phone):
    accounts = await db.b_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


@router.callback_query(F.data == 'tg_accs_monitor', KnownUser())
async def input_monitor(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    logger.info('awaiting acc to set monitor')
    accounts = await db.db_get_all_tg_accounts()
    cur_monitor = '\n'.join(await db.db_get_monitor_account()) or 'Нет'
    await callback.message.answer(f'Аккаунты для мониторинга: \n{cur_monitor}\n'
                                  'Выберите аккаунт, который будет мониторить каналы:',
                                  reply_markup=kb_admin.generate_accs_keyboard(accounts, 'monitor'))
    # #await callback.message.delete()


@router.callback_query(F.data.startswith('account_monitor'))
async def set_monitor_acc(callback: CallbackQuery):
    #await callback.message.delete()
    acc = callback.data.split('_')[-1]
    await db.db_remove_tg_account(acc)
    await db.db_add_tg_monitor_account(acc)
    await callback.message.answer('Аккаунт для мониторинга установлен.', reply_markup=kb_admin.tg_accs_btns())