from aiogram.types import CallbackQuery
from aiogram import Router, F
from keyboards import kb_admin
from database import db
from filters.known_user import KnownUser
from filters.sub_types import BasicSub
router = Router()
router.message.filter(
)

@router.callback_query(F.data == 'settings')
async def process_settings(callback: CallbackQuery):
    uid = callback.from_user.id
    accounts = len(await db.get_user_accounts(uid)) or '0'
    channels = len(await db.db_get_all_telegram_channels(uid)) or '0'
    basic_members = await db.get_user_ids_by_sub_type('DEMO')
    if callback.from_user.id in basic_members:
        print('basic_sub')
        await callback.message.answer(text=f'<b>Настройки:</b>\n\n'
                                           f'<b>Внесено каналов:</b> {channels}\n'
                                           f'<b>Доступно Telegram аккаунтов:</b> 1 (демо-период)\n',
                                      reply_markup=kb_admin.settings_btns(),
                                      parse_mode='HTML')
    else:
        await callback.message.answer(text=f'<b>Настройки:</b>\n\n'
                                           f'<b>Внесено каналов:</b> {channels}\n'
                                           f'<b>Доступно Telegram аккаунтов:</b> {accounts}\n',
                                      reply_markup=kb_admin.settings_btns(),
                                      parse_mode='HTML')



@router.callback_query(F.data == 'back_to_settings')
async def back_to_settings(callback: CallbackQuery):
    uid = callback.from_user.id
    accounts = len(await db.get_user_accounts(uid)) or '0'
    channels = len(await db.db_get_all_telegram_channels(uid)) or '0'
    basic_members = await db.get_user_ids_by_sub_type('DEMO')
    if callback.from_user.id in basic_members:
        await callback.message.answer(text=f'<b>Настройки:</b>\n\n'
                                           f'<b>Внесено каналов:</b> {channels}\n'
                                           f'<b>Доступно Telegram аккаунтов:</b> 1 (демо-период)\n',
                                      reply_markup=kb_admin.settings_btns(),
                                      parse_mode='HTML')
    else:
        await callback.message.answer(text=f'<b>Настройки:</b>\n\n'
                                           f'<b>Внесено каналов:</b> {channels}\n'
                                           f'<b>Доступно Telegram аккаунтов:</b> {accounts}\n',
                                      reply_markup=kb_admin.settings_btns(),
                                      parse_mode='HTML')