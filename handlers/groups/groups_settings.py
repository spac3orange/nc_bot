from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import group_settings_btns
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
router = Router()


@router.callback_query(F.data == 'groups_settings')
async def groups_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('Настройки телеграм каналов:\n\n'
                                  'Информация: /help_channels', reply_markup=group_settings_btns())


@router.callback_query(F.data == 'back_to_groups')
async def back_groups_settings(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
    await state.clear()