import random
import asyncio
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
from database.db_action import db_add_tg_account, db_get_all_tg_accounts, db_get_all_telegram_groups
from handlers.groups.add_group import all_accs_join_channel
from telethon import errors
router = Router()


async def acc_in_table(phone):
    accounts = await db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False

async def join_all_channels(session, message, phone):
    all_channels = await db_get_all_telegram_groups()
    if all_channels:
        for i, chnl in enumerate(all_channels, 1):
            if i in [5, 9, 13]:
                slp = random.randint(480, 560)
                await message.answer(
                    'После вступления в 4 канала подряд требуется перерыв.\n'
                    f'Запущено ожидание {slp} секунд.'
                )
                await asyncio.sleep(slp)
            res = await session.join_group(chnl)
            if res == 'already in group':
                await message.answer(f'{phone} уже состоит в канале {chnl}')
            elif res == 'banned':
                await message.answer(f'{phone} заблокирован')
            elif res == 'joined':
                await message.answer(f'{phone} успешно вступил в канал {chnl}')
            else:
                await message.answer(f'{phone} ошибка при вступлении в канал {chnl}')
    else:
        await message.answer('Нет добавленных каналов.')

@router.callback_query(F.data == 'tg_accs_add')
async def input_phone(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting phone to add telegram account')
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите номер телефона: ', reply_markup=tg_back())
    await state.set_state(AddTgAccState.input_2fa)
    print(await state.get_state())


@router.message(AddTgAccState.input_2fa)
async def input_2fa(message: Message, state: FSMContext):
    await message.answer('Введите пароль 2fa:\n'
                         'Если пароль не установлен, введите "нет"')
    await state.update_data(phone=message.text)
    await state.set_state(AddTgAccState.input_number)


@router.message(AddTgAccState.input_number)
async def input_code(message: Message, state: FSMContext):
    await state.update_data(password=message.text)

    data = await state.get_data()
    phone = data['phone']
    print(phone)
    if not await acc_in_table(phone):
        logger.info('awaiting for auth code in telegram')
        await message.answer('Запрашиваю код подтверждения...')
        auth = AuthTelethon(phone)
        await state.update_data(tg_client=auth)
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
    try:
        data = await state.get_data()
        print(data)
        password = data['password']
        print(password)
        await data['tg_client'].login_process_code(message.text)
        await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
        await message.answer('Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())
        await db_add_tg_account(data['phone'])
        logger.info('telegram account successfully added to db')

        await message.answer('Запущено вступление во все добавленные в базу каналы')
        await join_all_channels(data['tg_client'], message, data['phone'])

    except errors.SessionPasswordNeededError as e:
        try:
            logger.error(e)
            await data['tg_client'].login_process_code(password=password)
            await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
            await message.answer('Настройки телеграм аккаунтов:', reply_markup=tg_accs_btns())
            await db_add_tg_account(data['phone'])
            logger.info('telegram account successfully added to db')

            await message.answer('Запущено вступление во все добавленные в базу каналы')
            await join_all_channels(data['tg_client'], message, data['phone'])
        except Exception as e:
            logger.error(e)
            await message.answer('Ошибка логина. Пожалуйста, попробуйте еще раз.')
            return

    await state.clear()
