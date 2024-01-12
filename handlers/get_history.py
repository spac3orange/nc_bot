from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from data.logger import logger
from filters.known_user import KnownUser
from aiogram.types import FSInputFile
import os
router = Router()
router.message.filter(
    KnownUser()
)

async def get_full_history(uid):
    path = f'history/history_{uid}.txt'
    if os.path.exists(path):
        file = FSInputFile(path)
        return file
    return False

@router.callback_query(F.data == 'get_history', KnownUser())
async def get_history(callback: CallbackQuery):
    uid = callback.from_user.id
    history_path = f'history/history_462813109.txt'
    try:
        with open(history_path, encoding='utf-8') as file:
            history = file.read()
            history = history.split('|')
            print(len(history))
            history = history[-10:] if len(history) >= 10 else history
        if history:
            for i in history:
                if len(i) > 1 and i != '\n' and i != ' ' and i != '':
                    await callback.message.answer(i, parse_mode='HTML')
        else:
            await callback.message.answer('История не найдена.')
    except Exception as e:
        logger.error(e)
        await callback.message.answer('История не найдена.')

@router.message(Command('full_history'))
async def send_full_history(message: Message):
    file = await get_full_history('462813109')
    if file:
        await message.answer_document(file, caption='Полная история отправленных комментариев')
    else:
        await message.answer('Файл истории не найден')
