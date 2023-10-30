from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect
from database.db_action import db_get_all_tg_accounts, db_get_monitor_account
from typing import List, Tuple
router = Router()


async def get_info(accounts: list) -> List[Tuple[str]]:
    accs_info = []
    for session in accounts:
        try:
            sess = TelethonConnect(session)
            accs_info.append(await sess.get_info())
        except Exception as e:
            print(e)
    return accs_info


@router.callback_query(F.data == 'tg_accs_status')
async def get_acc_info(callback: CallbackQuery, state: FSMContext):
    logger.info('getting info about TG accounts')
    await callback.message.answer('Запрашиваю информацию о подключенных аккаунтах...')
    try:
        accounts = await db_get_all_tg_accounts()
        displayed_accounts = '\n'.join(accounts)
        monitor = ''.join(await db_get_monitor_account())
        if accounts:
            accs_info = await get_info(accounts)

            accounts_formatted = '\n\n'.join([
                                              f'Тел: {phone}'
                                              f'\nID: {id}'
                                              f'\nИмя: {name}'
                                              f'\nФамилия: {surname}'
                                              f'\nНик: {username}'
                                              f'\nОграничения: {restricted}'
                                              for phone, id, name, surname, username, restricted in accs_info])

            await callback.message.answer(text=f'Аккаунт для мониторинга:\n{monitor}\n\n'
                                               f'Аккануты:\n{displayed_accounts}\n\nИнфо:\n{accounts_formatted}')
        else:
            await callback.message.answer('Нет подключенных аккаунтов.')
    except Exception as e:
        logger.error(e)
