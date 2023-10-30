from aiogram.types import Message, CallbackQuery
from data.logger import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from keyboards import tg_accs_btns, tg_back
from filters.is_admin import IsAdmin
from aiogram.fsm.context import FSMContext
from states.states import AddTgAccState
from data.config_telethon_scheme import AuthTelethon
from database.db_action import db_add_tg_account, db_get_all_tg_accounts
router = Router()


async def acc_in_table(phone):
    accounts = await db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


@router.callback_query(F.data == 'tg_accs_add')
async def input_phone(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting phone to add telegram account')
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите номер телефона: ', reply_markup=tg_back())
    await state.set_state(AddTgAccState.input_number)
    print(await state.get_state())


@router.message(AddTgAccState.input_number)
async def input_code(message: Message, state: FSMContext):
    phone = message.text
    if not await acc_in_table(phone):
        logger.info('awaiting for auth code in telegram')
        await message.answer('Запрашиваю код подтверждения...')
        auth = AuthTelethon(message.text)
        await state.update_data(tg_client=auth, phone=message.text)
        if await auth.login_phone():
            await message.answer('Код подтверждения отправлен.\n'
                                 'Пожалуйста, проверьте телеграм и введите код:')
        else:
            await message.answer('Ошибка при попытке отправить код подтверждения.')
            await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())
        await state.set_state(AddTgAccState.input_code)
    else:
        logger.error(f'account with phone {phone} already exists in db')
        await message.answer(f'Аккаунт с номером {phone} уже существует в базе данных.')
        await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())


@router.message(StateFilter(AddTgAccState.input_code))
async def add_tg_acc(message: Message, state: FSMContext):
    data = await state.get_data()
    await data['tg_client'].login_process_code(message.text)
    await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
    await message.answer('Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())
    await db_add_tg_account(data['phone'])
    logger.info('telegram account successfully added to db')
    await state.clear()
