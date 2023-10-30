from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import settings_btns
from filters.is_admin import IsAdmin
router = Router()


@router.callback_query(F.data == 'settings')
async def process_start(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer(text='Настройки:\n\n'
                                       'Информация: /help_settings', reply_markup=settings_btns())


@router.callback_query(F.data == 'back_to_settings')
async def back_to_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer(text='Настройки:', reply_markup=settings_btns())