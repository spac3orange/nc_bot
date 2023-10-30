from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from data import logger
from aiogram import Router, F
from keyboards import start_btns
from filters.is_admin import IsAdmin
router = Router()


@router.message(CommandStart, IsAdmin(F))
async def process_start(message: Message):
    await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
    await message.answer('Добро пожаловать!', reply_markup=start_btns())
    logger.info(f'@{message.from_user.username} connected')


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer(text='Welcome', reply_markup=start_btns())