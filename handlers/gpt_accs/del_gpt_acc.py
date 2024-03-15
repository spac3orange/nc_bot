from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from data.logger import logger
from database import db
from filters.is_admin import IsAdmin
from keyboards import kb_admin

router = Router()
router.message.filter(
    IsAdmin(F)
)



@router.callback_query(F.data == 'gpt_accs_del')
async def del_gpt_acc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    api_keys = await db.db_get_all_gpt_accounts()
    #await callback.message.delete()
    await callback.message.answer('Выберите ключ, который будет удален: ',
                                  reply_markup=kb_admin.generate_gpt_accs_keyboard(api_keys))


@router.callback_query(F.data.startswith('gpt_del_'))
async def gpt_acc_deleted(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    gpt_key = callback.data.split('_')[-1]
    await db.db_remove_gpt_account(gpt_key)
    #await message.delete()
    logger.info('gpt account deleted from db')
    await callback.message.answer('Аккаунт удален из базы данных')
    await callback.message.answer('Настройки ChatGPT аккаунтов:', reply_markup=kb_admin.gpt_accs_btns())
