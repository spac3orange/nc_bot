from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from data.logger import logger
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'get_history', KnownUser())
async def get_history(callback: CallbackQuery):
    uid = callback.from_user.id
    history_path = f'history/history_{uid}.txt'
    try:
        with open(history_path, encoding='utf-8') as file:
            history = file.read()
            history = history.split('|')
            print(len(history))
            history = history[-10:] if len(history) >= 10 else history
            history = '\n'.join(history)
        if history:
            await callback.message.answer(text=history)
        else:
            await callback.message.answer('История не найдена.')
    except Exception as e:
        logger.error(e)
        await callback.message.answer('История не найдена.')


