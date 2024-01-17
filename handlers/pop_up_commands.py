from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import user_license

router = Router()


@router.message(Command(commands='user_license'))
async def send_user_license(message: Message):
    await message.answer(text=user_license.license_text, parse_mode='HTML')
