from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import generate_group_keyboard, promt_settings, group_settings_btns, groups_back
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import EditPromts
from database.db_action import (db_add_telegram_group, db_get_all_telegram_groups, db_get_promts_for_group,
                                db_add_promts_for_group)
from data.config_aiogram import aiogram_bot
router = Router()


@router.callback_query(F.data == 'groups_promts')
async def promt_choose_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    groups = await db_get_all_telegram_groups()
    await callback.message.answer('Выберите канал: ', reply_markup=generate_group_keyboard(groups, 'promts'))


@router.callback_query(F.data.startswith('promts'))
async def group_promts(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    group = callback.data.split('[[')[-1]
    await state.update_data(group_name=group)
    promt = await db_get_promts_for_group(group) or 'Нет'
    await callback.message.answer(f'<b>Выбрана группа:</b> {group}\n\n'
                                  f'<b>Текущий установленный промт</b>: \n{promt}',
                                  reply_markup=promt_settings(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'group_edit_promt')
async def set_promt(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await state.update_data(message_id=callback.message.message_id)
    data = await state.get_data()
    await callback.message.answer(f'Пожалуйста введите новый промт для группы: {data["group_name"]}', reply_markup=groups_back())
    await state.set_state(EditPromts.edit_promt)


@router.message(EditPromts.edit_promt)
async def promt_updated(message: Message, state: FSMContext):
    data = await state.get_data()
    await db_add_promts_for_group(data["group_name"], message.text)
    await message.answer('Промт успешно установлен.')
    await message.answer('Настройки телеграм каналов: ', reply_markup=group_settings_btns())
    await state.clear()


