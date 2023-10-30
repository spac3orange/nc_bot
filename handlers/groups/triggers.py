from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import generate_group_keyboard, promt_settings, triggers_settings, group_settings_btns
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import Triggers
from database.db_action import (db_get_all_telegram_groups, db_add_trigger_for_group,
                                db_get_triggers_for_group, db_remove_triggers_for_group)
from data.config_aiogram import aiogram_bot
router = Router()


@router.callback_query(F.data == 'groups_triggers')
async def trigger_choose_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    groups = await db_get_all_telegram_groups()
    await callback.message.answer('Выберите канал: ', reply_markup=generate_group_keyboard(groups, 'triggers'))


@router.callback_query(F.data.startswith('triggers'))
async def group_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    group = callback.data.split('[[')[-1]
    await state.update_data(group_name=group)
    triggers = await db_get_triggers_for_group(group) or 'Нет'

    await callback.message.answer(f'Выбрана группа: {group}\n\n'
                                  f'Установленные триггеры: \n\n{triggers}',
                                  reply_markup=triggers_settings())


@router.callback_query(F.data == 'group_add_triggers')
async def add_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Введите добавляемые триггеры через запятую:')
    await state.set_state(Triggers.add_trigger)


@router.message(Triggers.add_trigger)
async def triggers_added(message: Message, state: FSMContext):
    data = await state.get_data()
    triggers = message.text.lower().split(',')
    triggers = [x.strip() for x in triggers]
    await db_add_trigger_for_group(data["group_name"], triggers)
    await message.answer('Триггеры обновлены.', reply_markup=group_settings_btns())
    await state.clear()


@router.callback_query(F.data == 'group_del_triggers')
async def del_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Введите удаляемые триггеры через запятую:')
    await state.set_state(Triggers.del_trigger)


@router.message(Triggers.del_trigger)
async def triggers_deleted(message: Message, state: FSMContext):
    data = await state.get_data()
    triggers = message.text.lower().split(',')
    triggers = [x.strip() for x in triggers]
    await db_remove_triggers_for_group(data["group_name"], triggers)
    await message.answer('Триггеры обновлены.', reply_markup=group_settings_btns())
    await state.clear()