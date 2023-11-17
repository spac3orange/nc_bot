import asyncio
import random

from aiogram.types import CallbackQuery
from aiogram import Router, F
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect
from database import db
from keyboards import kb_admin
router = Router()



@router.callback_query(F.data == 'tg_accs_join_groups')
async def accs_join_groups(callback: CallbackQuery):
    #await callback.message.delete()
    accounts = await db.db_get_all_tg_accounts()
    monitor = await db.db_get_monitor_account()
    accounts.extend(monitor)
    groups = await db.db_get_all_telegram_channels(uid)
    if accounts and groups:
        await callback.message.answer('Запуск вступления в группы.\n\n'
                                      'Это может занять несколько минут.')
        for acc in accounts:
            try:
                sess = TelethonConnect(acc)
                for group in groups:
                    res = await sess.join_group(group)

                    print(res)
                    if res == 'already_in_group':
                        await callback.message.answer(f'{acc} уже состоит в группе {group}')
                        continue
                    elif res == 'joined':
                        await callback.message.answer(f'{acc} успешно вступил в группу {group}')
                    elif res == 'banned':
                        await callback.message.answer(f'{acc} был заблокирован')
                        continue
                    else:
                        await callback.message.answer(f'{acc} ошибка при вступлении в группу')
                    slp = random.randint(10, 15)
                    await callback.message.answer(f'Ожидаю {slp} секунд...')
                    await asyncio.sleep(slp)

                await callback.message.answer('Процесс вступления в каналы завершен.',
                                              reply_markup=kb_admin.settings_btns())
            except Exception as e:
                logger.error(e)
                continue


    else:
        await callback.message.answer('Не найдено аккаунтов или каналов в базе данных\n'
                                      'Пожалуйста, проверьте настройки и попробуйте еще раз.')
        await callback.message.answer('Настройки', reply_markup=kb_admin.settings_btns())
