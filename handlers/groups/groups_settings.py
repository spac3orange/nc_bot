from aiogram.types import CallbackQuery
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from filters.known_user import KnownUser
from database import db
router = Router()
router.message.filter(
)


@router.callback_query(F.data == 'groups_settings', KnownUser())
async def groups_settings(callback: CallbackQuery):
    await callback.answer()
    #await callback.message.delete()
    uid = callback.from_user.id
    groups = '\n'.join(await db.db_get_all_telegram_channels(uid))

    await callback.message.answer('<b>Настройки телеграм каналов:</b>\n\n'
                                  f'Ваши каналы:\n'
                                  f'{len(groups)}\n\n'
                                  'Информация: /help_channels',
                                  reply_markup=kb_admin.group_settings_btns(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'back_to_groups')
async def back_groups_settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # await callback.message.delete()
    uid = callback.from_user.id
    groups = '\n'.join(await db.db_get_all_telegram_channels(uid))
    await callback.message.answer('<b>Настройки телеграм каналов:</b>\n\n'
                                  'Ваши каналы:\n'
                                  f'{len(groups)}\n\n'
                                  'Информация: /help_channels',
                                  reply_markup=kb_admin.group_settings_btns(),
                                  parse_mode='HTML')