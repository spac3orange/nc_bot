from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from database import db
from aiogram.fsm.context import FSMContext
from data import logger
from utils import user_license

router = Router()


@router.message(Command(commands='user_license'))
async def send_user_license(message: Message):
    await message.answer(text=user_license.license_text, parse_mode='HTML')
