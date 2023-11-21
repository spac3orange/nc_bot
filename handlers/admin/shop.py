from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from data import logger
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from utils.scheduler import monitor
from database import db
router = Router()
router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'admin_shop')
async def process_admin_shop(callback: CallbackQuery):
    await callback.message.answer(f'В разработке.')