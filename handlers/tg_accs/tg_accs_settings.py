from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import tg_accs_btns
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
router = Router()


@router.callback_query(F.data == 'tg_accs')
async def tg_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('Настройки телеграм аккаунтов:\n\n'
                                  'Информация: /help_tg_accs', reply_markup=tg_accs_btns())


@router.callback_query(F.data == 'back_to_accs')
async def back_to_accs(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())
    await state.clear()