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
from database.db_action import db_get_all_telegram_groups
router = Router()


@router.callback_query(F.data == 'groups_info')
async def get_all_groups(callback: CallbackQuery):
    groups = await db_get_all_telegram_groups()
    if groups:
        await callback.message.answer('\n'.join(groups))
    else:
        await callback.message.answer('Каналы не найдены.')

