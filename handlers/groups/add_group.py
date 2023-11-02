from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import group_settings_btns, groups_back
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import AddGroup
from database.db_action import db_add_telegram_group, db_get_all_telegram_grp_id, db_get_all_tg_accounts, db_get_monitor_account
from data.config_telethon_scheme import TelethonConnect
from data.config_aiogram import aiogram_bot
router = Router()


async def group_in_table(group_id):
    group_ids = await db_get_all_telegram_grp_id()
    if group_id in group_ids:
        return True
    return False


async def get_channel_id(link: str) -> int:
    chat = await aiogram_bot.get_chat(link)
    return chat.id


async def all_accs_join_channel(message, group_link):
    accounts = await db_get_all_tg_accounts()
    monitor = await db_get_monitor_account()
    if accounts:
        for acc in accounts:
            session = TelethonConnect(acc)
            res = await session.join_group(group_link)
            if res == 'already in group':
                await message.answer(f'{acc} уже состоит в канале {group_link}')
            elif res == 'banned':
                await message.answer(f'{acc} заблокирован')
            elif res == 'joined':
                await message.answer(f'{acc} успешно вступил в канал {group_link}')
            else:
                await message.answer(f'{acc} ошибка при вступлении в канал {group_link}')

        for mon in monitor:
            session = TelethonConnect(mon)
            res = await session.join_group(group_link)
            if res == 'already in group':
                await message.answer(f'{mon} уже состоит в канале {group_link}')
            elif res == 'banned':
                await message.answer(f'{mon} заблокирован')
            elif res == 'joined':
                await message.answer(f'{mon} успешно вступил в канал {group_link}')
            else:
                await message.answer(f'{mon} ошибка при вступлении в канал {group_link}')
    else:
        await message.answer('Нет добавленных аккаунтов')
        return


@router.callback_query(F.data == 'groups_add')
async def input_group(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите ссылку на канал в поддерживаемом формате:\n\n'
                                  'Формат:\n@channel_name', reply_markup=groups_back())
    await state.set_state(AddGroup.input_group)
    print(await state.get_state())


@router.message(AddGroup.input_group)
async def add_group(message: Message, state: FSMContext):
    try:
        group_name = message.text
        group_id = await get_channel_id(group_name)
        print(group_id)
        if not await group_in_table(group_id):
            await db_add_telegram_group(group_name, group_id)
            await message.answer('Канал добавлен в базу данных.')
            await message.answer('Запущено вступление аккаунтов в канал')

            await all_accs_join_channel(message, group_name)
            await message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
            logger.info(f'Group {group_name} added to database')

        else:
            await message.answer(f'Канал {group_name} уже существует в базе данных.')
            await message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
            logger.info(f'Group {group_name} already exists in database')
        await state.clear()
    except Exception as e:
        logger.error(e)
        await message.answer('Канал не найден')
