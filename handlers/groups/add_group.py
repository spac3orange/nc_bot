from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import group_settings_btns, groups_back
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import AddGroup
from database.db_action import db_add_telegram_group, db_get_all_telegram_groups
router = Router()


async def group_in_table(group_link):
    groups = await db_get_all_telegram_groups()
    if group_link in groups:
        return True
    return False


@router.callback_query(F.data == 'groups_add')
async def input_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите ссылку на канал в поддерживаемом формате:\n\n'
                                  'Формат:\n@group_name\nhttps://t.me/group_name', reply_markup=groups_back())
    await state.set_state(AddGroup.input_group)
    print(await state.get_state())


@router.message(AddGroup.input_group)
async def add_group(message: Message, state: FSMContext):
    await message.delete()
    group = message.text
    if not await group_in_table(group):
        await db_add_telegram_group(group)
        await message.answer('Канал добавлен в базу данных.')
        await message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
        logger.info(f'Group {group} added to database')

    else:
        await message.answer(f'Канал {group} уже существует в базе данных.')
        await message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
        logger.info(f'Group {group} already exists in database')
    await state.clear()