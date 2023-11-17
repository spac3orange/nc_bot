from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from keyboards import kb_admin
from data.logger import logger
from filters.known_user import KnownUser
from database import db
router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'notifications_settings')
async def notifications_menu(callback: CallbackQuery):
    uid = callback.from_user.id
    notif_status = await db.get_user_notifications_status(uid)
    await callback.message.answer('<b>Настройки уведомлений:</b>\n\n'
                                  f'<b>Уведомления:</b> {"Включены🟢" if notif_status else "Выключены🔴"}',
                                  reply_markup=kb_admin.notifications_menu(), parse_mode='HTML')


@router.callback_query(F.data == 'notif_enable')
async def enable_notifications(callback: CallbackQuery):
    uid = callback.from_user.id
    await db.toggle_user_notifications(uid, True)
    await callback.message.answer('Уведомления включены🟢')


@router.callback_query(F.data == 'notif_disable')
async def disable_notifications(callback: CallbackQuery):
    uid = callback.from_user.id
    await db.toggle_user_notifications(uid, False)
    await callback.message.answer('Уведомления выключены🔴')

