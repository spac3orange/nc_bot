from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from aiogram.fsm.context import FSMContext
from database import db
router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'tg_accs', KnownUser())
async def tg_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    accounts_free = await db.db_get_all_tg_accounts()
    accounts_paid = await db.get_all_paid_accounts()
    paid_string = ''
    if accounts_paid:
        for k, v in accounts_paid.items():
            uid = k.split('_')[1]
            username = await db.get_username_by_user_id(int(uid))
            paid_string += f'\n<b>Username</b>: {username}\n<b>UID</b>: {uid}\n<b>Количество аккаунтов</b>: {len(v)}\n'

    await callback.message.answer('<b>Настройки телеграм аккаунтов:</b>\n\n'
                                  f'<b>Аккаунты пользователей с подпиской:</b> {paid_string or "0"}\n\n'
                                  f'<b>Доступно бесплатных аккаунтов:</b> {len(accounts_free)}\n\n'
                                  'Информация: /help_tg_accs', reply_markup=kb_admin.tg_accs_btns(), parse_mode='HTML')


@router.callback_query(F.data == 'back_to_accs')
async def back_to_accs(callback: CallbackQuery, state: FSMContext):
    accounts_free = await db.db_get_all_tg_accounts()
    accounts_paid = await db.get_all_paid_accounts()
    await callback.message.answer('<b>Настройки телеграм аккаунтов:</b>\n\n'
                                  f'<b>Аккаунты пользователей с подпиской:</b> {len(accounts_paid)}\n\n'
                                  f'<b>Доступно бесплатных аккаунтов:</b> {len(accounts_free)}\n\n'
                                  'Информация: /help_tg_accs', reply_markup=kb_admin.tg_accs_btns(), parse_mode='HTML')