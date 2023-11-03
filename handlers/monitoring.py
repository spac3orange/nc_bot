from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from keyboards import start_btns
from data.logger import logger
from bot import monitor
router = Router()


@router.callback_query(F.data == 'monitoring_start')
async def monitoring_start(callback: CallbackQuery):
    try:
        await callback.message.answer('Мониторинг запущен.')
        await monitor.start_monitoring()
    except Exception as e:
        logger.error(e)
        await callback.message.answer('Ошибка.\n'
                                      'Аккаунт для мониторинга не установлен.')


@router.callback_query(F.data == 'monitoring_stop')
async def monitoring_stop(callback: CallbackQuery):
    await callback.message.answer('Мониторинг остановлен.')
    await monitor.stop_monitoring()


@router.message(Command(commands='monitor_status'))
async def get_monitor_status(message: Message):
    status = await monitor.get_status()
    if status:
        await message.answer(f'Мониторинг работает.')
    else:
        await message.answer(f'Мониторинг не работает.')