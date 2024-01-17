import asyncio
from aiogram.types import CallbackQuery
from data.logger import logger
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from database import db, accs_action
from data.chat_gpt import AuthOpenAI
from filters.is_admin import IsAdmin
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def gpt_acc_in_table(phone):
    accounts = await accs_action.db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


@router.callback_query(F.data == 'gpt_accs_info')
async def get_info_gpt_accs(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting info about gpt accs')
    #await callback.message.delete()
    await callback.message.answer('Запрашиваю информацию о API ключах...')
    api_keys = await db.db_get_all_gpt_accounts()
    keys_status = dict()
    keys_status_list = []
    if api_keys:
        tasks = []
        for key in api_keys:
            gpt_acc = AuthOpenAI(key)
            task = asyncio.create_task(gpt_acc.check_work())
            tasks.append(task)
        result = await asyncio.gather(*tasks)
        if result:
            for key, value in zip(api_keys, result):
                if value == 'Аккаунт доступен.':
                    value = 'Аккаунт доступен 🟢'
                else:
                    value = 'Аккаунт не доступен 🔴'
                keys_status_list.append(f'<b>Ключ:</b> {key}\n<b>Статус:</b> {value}')

        for key in keys_status_list:
            await callback.message.answer(text=key, parse_mode='HTML')
        # await callback.message.answer(text=f'<b>API</b> ключи:\n\n{keys_status_list}', reply_markup=kb_admin.gpt_back(),
        #                               parse_mode='HTML')
    else:
        await callback.message.answer(text=f'Нет добавленных API ключей.')
        await callback.message.answer(text=f'Настройки телеграм аккаунтов:.', reply_markup=kb_admin.gpt_accs_btns())


