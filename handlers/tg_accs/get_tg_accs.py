from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect
from database import db
from typing import List, Tuple
from filters.known_user import KnownUser
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


@router.callback_query(F.data == 'tg_accs_status', KnownUser())
async def get_acc_info(callback: CallbackQuery, state: FSMContext):
    logger.info('getting info about TG accounts')
    await callback.message.answer('Запрашиваю информацию о подключенных аккаунтах...')
    try:
        accounts = await db.db_get_all_tg_accounts()
        displayed_accounts = '\n'.join(accounts)
        monitor = ''.join(await db.db_get_monitor_account())
        if accounts:
            accs_info = await get_info(accounts)
            monitor_info = await get_info([monitor])
            monitor_formatted = '\n\n'.join([
                                                f'<b>Тел:</b> {phone}'
                                                f'\n<b>ID:</b> {id}'
                                                f'\n<b>Имя:</b> {name}'
                                                f'\n<b>Фамилия:</b> {surname}'
                                                f'\n<b>Ник:</b> {username}'
                                                f'\n<b>Био:</b> {about}'
                                                f'\n<b>Ограничения:</b> {restricted}'
                                                for phone, id, name, surname, username, restricted, \
                                                        about in monitor_info])
            accounts_formatted = '\n\n'.join([
                                              f'<b>Тел:</b> {phone}'
                                              f'\n<b>ID:</b> {id}'
                                              f'\n<b>Имя:</b> {name}'
                                              f'\n<b>Фамилия:</b> {surname}'
                                              f'\n<b>Ник:</b> {username}'
                                              f'\n<b>Био:</b> {about}'
                                              f'\n<b>Ограничения:</b> {restricted}'
                                              for phone, id, name, surname, username, restricted, about in accs_info])

            await callback.message.answer(text=f'<b>Аккаунт для мониторинга:</b>\n{monitor}\n\n<b>Инфо:</b>\n'
                                               f'{monitor_formatted}\n\n'
                                               f'<b>Аккануты:</b>\n{displayed_accounts}\n\n<b>Инфо:</b>\n'
                                               f'{accounts_formatted}', parse_mode='HTML')
        else:
            await callback.message.answer('Нет подключенных аккаунтов.')
    except Exception as e:
        logger.error(e)
