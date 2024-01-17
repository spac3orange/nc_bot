from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from data.logger import logger
from database import db
from filters.known_user import KnownUser

router = Router()
router.message.filter(
)





@router.callback_query(F.data == 'monitoring_start_users', KnownUser())
async def monitoring_start(callback: CallbackQuery):
    try:
        uid = callback.from_user.id
        await db.toggle_monitoring_status(uid, True)
        await callback.message.answer('Статус: <b>Работает🟢</b>', parse_mode='HTML')
    except Exception as e:
        logger.error(e)
        await callback.message.answer('Ошибка.\n'
                                      'Аккаунт для мониторинга не установлен.')


@router.callback_query(F.data == 'monitoring_stop_users', KnownUser())
async def monitoring_stop(callback: CallbackQuery):
    uid = callback.from_user.id
    await db.toggle_monitoring_status(uid, False)
    await callback.message.answer('Статус: <b>Выключен🔴</b>', parse_mode='HTML')


@router.message(Command(commands='monitoring_status'))
async def get_monitor_status(message: Message):
    uid = message.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)
    if user_monitoring_status:
        await message.answer(f'Статус: <b>Работает🟢</b>', parse_mode='HTML')
    else:
        await message.answer('Статус: <b>Выключен🔴</b>', parse_mode='HTML')


