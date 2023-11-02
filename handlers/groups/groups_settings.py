from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import group_settings_btns
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from database.db_action import db_get_all_telegram_groups, db_get_all_telegram_ids, db_get_triggers_for_group, db_get_promts_for_group
router = Router()


@router.callback_query(F.data == 'groups_settings')
async def groups_settings(callback: CallbackQuery):
    #await callback.message.delete()
    groups = await db_get_all_telegram_groups()
    grp_dict = {}
    for grp in groups:
        triggers = await db_get_triggers_for_group(grp)
        promts = await db_get_promts_for_group(grp)
        grp_dict[grp] = ['🟢' if triggers else '🔴', '🟢' if promts else '🔴']

    string = ''
    for k, v in grp_dict.items():
        string += '\n' + k + f'\n<b>Триггеры:</b> {v[0]} <b>Промт:</b> {v[1]}'

    await callback.message.answer('Настройки телеграм каналов:\n'
                                  f'{string}\n\n'
                                  'Информация: /help_channels',
                                  reply_markup=group_settings_btns(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'back_to_groups')
async def back_groups_settings(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Настройки телеграм каналов:', reply_markup=group_settings_btns())
    await state.clear()