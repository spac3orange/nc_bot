from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from keyboards import kb_admin

router = Router()
router.message.filter(
)


@router.callback_query(F.data == 'notifications_settings')
async def notifications_menu(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    notif_status = await db.get_user_notifications_status(uid)
    await callback.message.answer('<b>Настройки уведомлений:</b>\n\n'
                                  f'<b>Уведомления:</b> {"Включены🟢" if notif_status else "Выключены🔴"}',
                                  reply_markup=kb_admin.notifications_menu(), parse_mode='HTML')


@router.callback_query(F.data == 'notif_enable')
async def enable_notifications(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    await db.toggle_user_notifications(uid, True)
    await callback.message.answer('Уведомления включены🟢')


@router.callback_query(F.data == 'notif_disable')
async def disable_notifications(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    await db.toggle_user_notifications(uid, False)
    await callback.message.answer('Уведомления выключены🔴')

