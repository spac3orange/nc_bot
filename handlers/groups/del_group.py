from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import group_settings_btns, generate_group_keyboard
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext

from states.states import DelGroup
from data.config_telethon_scheme import AuthTelethon
from database.db_action import db_remove_telegram_group, db_get_all_telegram_groups
from .add_group import group_in_table
router = Router()


@router.callback_query(F.data == 'groups_del')
async def del_input_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    groups = await db_get_all_telegram_groups()
    await callback.message.answer('Выберите канал: ', reply_markup=generate_group_keyboard(groups, 'delete'))


@router.callback_query(F.data.startswith('delete'))
async def group_triggers(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    group = callback.data.split('[[')[-1]
    await db_remove_telegram_group(group)
    await callback.message.answer('Канал удален из базы данных.')
    await callback.message.answer('Настройки телеграм групп:', reply_markup=group_settings_btns())
    logger.info(f'group {group} was deleted from database')
    

# @router.message(DelGroup.input_group)
# async def group_deleted(message: Message, state: FSMContext):
#     group = message.text
#     if await group_in_table(group):
#         await db_remove_telegram_group(group)
#         await message.answer('Группы удалена из базы данных.')
#         await message.answer('Настройки телеграм групп:', reply_markup=group_settings_btns())
#         logger.info(f'group {group} was deleted from database')
#     else:
#         await message.answer('Группа не найдена в базе данных.')
#         await message.answer('Настройки телеграм групп:', reply_markup=group_settings_btns())
#         logger.error('group not found')
#     await state.clear()