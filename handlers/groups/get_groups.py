from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import tg_accs_btns
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import AddTgAccState
from data.config_telethon_scheme import AuthTelethon
from database.db_action import db_get_all_telegram_groups, db_get_all_telegram_ids
router = Router()


@router.callback_query(F.data == 'groups_info')
async def get_all_groups(callback: CallbackQuery):
    groups = await db_get_all_telegram_groups()
    group_ids = await db_get_all_telegram_ids()
    data = []
    for g, i in zip(groups, group_ids):
        data.append(g)
        data.append('<b>ID:</b> ' + str(i)[4:])

    if data:
        await callback.message.answer('\n'.join(data), parse_mode='HTML')
    else:
        await callback.message.answer('Каналы не найдены.')

