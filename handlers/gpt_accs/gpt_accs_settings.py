from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database import db
from filters.is_admin import IsAdmin
from keyboards import kb_admin

router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'gpt_accs')
async def gpt_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    gpt_accs = await db.db_get_all_gpt_accounts()
    await callback.message.answer(f'<b>Настройки ChatGPT аккаунтов:</b>\n\n'
                                  f'<b>API ключей в БД:</b> {str(len(gpt_accs))}\n\n',
                                  reply_markup=kb_admin.gpt_accs_btns(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'back_to_gpt')
async def gpt_accs_settings(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    gpt_accs = await db.db_get_all_gpt_accounts()
    await callback.message.answer(f'<b>Настройки ChatGPT аккаунтов:</b>\n\n'
                                  f'<b>API ключей в БД:</b> {str(len(gpt_accs))}\n\n'
                                  'Информация: /help_gpt_accs',
                                  reply_markup=kb_admin.gpt_accs_btns(),
                                  parse_mode='HTML')
    await state.clear()