from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import gpt_accs_btns
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
router = Router()


@router.callback_query(F.data == 'gpt_accs')
async def gpt_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('Настройки ChatGPT аккаунтов:\n\n'
                                  'Информация: /help_gpt_accs', reply_markup=gpt_accs_btns())


@router.callback_query(F.data == 'back_to_gpt')
async def gpt_accs_settings(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Настройки ChatGPT аккаунтов:', reply_markup=gpt_accs_btns())
    await state.clear()