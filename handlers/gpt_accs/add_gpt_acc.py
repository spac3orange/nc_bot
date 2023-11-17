from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from data.logger import logger
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from states.states import AddGPTAccState
from database import db
from filters.is_admin import IsAdmin
router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    if IsAdmin(F):
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'Мониторинг <b>{"выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'Мониторинг <b>{"выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')
    await state.clear()


async def gpt_acc_in_table(phone):
    accounts = await db.db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


async def check_gpt_key(api_key):
    return api_key.startswith('sk-')


@router.callback_query(F.data == 'gpt_accs_add')
async def input_gpt_acc(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting api key for gpt account')
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите API ключ ChatGPT: ', reply_markup=kb_admin.gpt_back())
    await state.set_state(AddGPTAccState.input_api)


@router.message(AddGPTAccState.input_api)
async def gpt_acc_added(message: Message, state: FSMContext):
    #await message.delete()
    api_key = message.text.strip()
    if await check_gpt_key(api_key):
        await db.db_add_gpt_account(api_key)
        await message.answer('API ключ добавлен в базу данных.')
        await message.answer('Настройки ChatGPT аккаунтов:', reply_markup=kb_admin.gpt_accs_btns())
    else:
        await message.answer('Введен не корректный API ключ.\n'
                             'Ключ должен начинаться с "-sk"\n'
                             'Пожалуйста, попробуйте еще раз\n'
                             'Отмена /cancel')
    await state.clear()