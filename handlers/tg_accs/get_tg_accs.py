import asyncio
import random
from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect
from database import db
from typing import List, Tuple
from filters.known_user import KnownUser
router = Router()


async def get_info(accounts: list, uid=None) -> List[Tuple[str]]:
    accs_info = []
    for session in accounts:
        try:
            slp = random.randint(3, 5)
            await asyncio.sleep(slp)
            sess = TelethonConnect(session)
            accs_info.append(await sess.get_info(uid=uid))
        except Exception as e:
            print(e)
    print(f'accs_info = {accs_info}')
    return accs_info


async def send_acc_info(acc, callback, user_id=None) -> None:
    try:
        if not user_id:
            acc_string = ''
            acc_info = await get_info([acc['phone']])
            print(acc_info)
            for phone, id, name, surname, username, restricted, about, sex in acc_info:
                acc_string += f'<b>Тел:</b> {phone}' \
                              f'\n<b>ID:</b> {id}' \
                              f'\n<b>Имя:</b> {name}' \
                              f'\n<b>Фамилия:</b> {surname}' \
                              f'\n<b>Пол:</b> {sex}' \
                              f'\n<b>Ник:</b> @{username}' \
                              f'\n<b>Био:</b> {about}' \
                              f'\n<b>Ограничения:</b> {restricted}' \
                              f'\n<b>Комментарии:</b> {acc["comments"]}'
                await callback.message.answer(acc_string, parse_mode='HTML')
                acc_string = ''
        else:
            acc_string = ''
            acc_info = await get_info([acc['phone']], user_id)  
            for phone, id, name, surname, username, restricted, about, sex in acc_info:
                acc_string += f'<b>Тел:</b> {phone}' \
                              f'\n<b>ID:</b> {id}' \
                              f'\n<b>Имя:</b> {name}' \
                              f'\n<b>Фамилия:</b> {surname}' \
                              f'\n<b>Пол:</b> {sex}' \
                              f'\n<b>Ник:</b> @{username}' \
                              f'\n<b>Био:</b> {about}' \
                              f'\n<b>Ограничения:</b> {restricted}' \
                              f'\n<b>Комментарии:</b> {acc["comments"]}'
                await callback.message.answer(acc_string, parse_mode='HTML')
                acc_string = ''
    except Exception as e:
        logger.error(e)
        await callback.message.answer(f'Ошибка при запросе информации об аккаунте {acc["phone"]}.'
                                      f'\nПожалуйста, попробуйте позднее.')

@router.callback_query(F.data == 'tg_accs_status', KnownUser())
async def get_acc_info(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    logger.info('getting info about TG accounts')
    await callback.message.answer('Запрашиваю информацию о подключенных аккаунтах...⏳')
    try:
        accounts = await db.db_get_all_tg_accounts_with_comments()
        print(accounts)
        if accounts:
            for table, value in accounts.items():
                if table == 'telegram_accounts':
                    await callback.message.answer('<b>Бесплатные аккаунты:</b>', parse_mode='HTML')
                    for acc in value:
                        await send_acc_info(acc, callback)

                elif table.startswith('accounts_'):
                    user_id = table.split('_')[-1]
                    await callback.message.answer(f'<b>Аккаунты пользователя {table.split("_")[-1]}:</b>', parse_mode='HTML')
                    for acc in value:
                        await send_acc_info(acc, callback, user_id)

        else:
            await callback.message.answer('Нет подключенных аккаунтов.')

    except Exception as e:
        logger.error(e)
