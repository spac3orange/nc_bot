from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot import monitor
from data.logger import logger
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from keyboards import kb_admin

router = Router()
router.message.filter(
    IsAdmin(F)
)




@router.callback_query(F.data == 'monitor_settings')
async def monitor_settings(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('<b>Глобальные настройки мониторинга</b>',
                                  reply_markup=kb_admin.monitoring_settings(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'monitoring_start', KnownUser())
async def monitoring_start(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.answer('Мониторинг запущен.')
        await monitor.start_monitoring()
    except Exception as e:
        logger.error(e)
        await callback.message.answer('Ошибка.\n'
                                      'Аккаунт для мониторинга не установлен.')


@router.callback_query(F.data == 'monitoring_stop', KnownUser())
async def monitoring_stop(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Мониторинг остановлен.')
    await monitor.stop_monitoring()


@router.message(Command(commands='monitor_status'))
async def get_monitor_status(message: Message):
    status = await monitor.get_status()
    if status:
        await message.answer(f'Мониторинг работает.')
    else:
        await message.answer(f'Мониторинг не работает.')


