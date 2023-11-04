from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from data import logger
from aiogram import Router, F
from keyboards import start_btns
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from .monitoring import monitor
from database.db_action import db_add_user
router = Router()


@router.message(CommandStart, KnownUser())
async def process_start(message: Message):
    status = await monitor.get_status()
    uid = message.from_user.id
    await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
    await message.answer('Добро пожаловать!\n\n'
                         f'Мониторинг <b>{"работает 🟢" if status else "выключен 🔴"}</b>',
                         reply_markup=start_btns(),
                         parse_mode='HTML')


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery):
    #await callback.message.delete()
    status = await monitor.get_status()
    await callback.message.answer('Добро пожаловать!\n\n'
                         f'Мониторинг <b>{"работает 🟢" if status else "выключен 🔴"}</b>',
                         reply_markup=start_btns(),
                         parse_mode='HTML')