from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from filters.is_admin import IsAdmin
from keyboards import kb_admin
from utils.scheduler import monitor

router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'admin_panel', IsAdmin(F))
async def process_admin_panel(callback: CallbackQuery):
    await callback.answer()
    status = await monitor.get_status()
    today_users = await db.db_get_users_today()
    await callback.message.answer(f'<b>Панель Администратора</b>\n\n'
                                  f'<b>Глобальный Мониторинг:</b> {"Запущен 🟢" if status else "Выключен 🔴"}\n'
                                  f'<b>Пользователей сегодня:</b> {len(today_users)}\n',

                                  reply_markup=kb_admin.admin_panel(),
                                  parse_mode='HTML')



