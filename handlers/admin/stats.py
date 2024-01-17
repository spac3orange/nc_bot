from aiogram import Router, F
from aiogram.types import CallbackQuery

from filters.is_admin import IsAdmin

router = Router()
router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'admin_stats')
async def process_admin_stats(callback: CallbackQuery):
    await callback.message.answer(f'В разработке.')