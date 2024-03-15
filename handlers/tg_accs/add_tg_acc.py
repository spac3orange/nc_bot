import asyncio
import os
from aiogram.types import Message, CallbackQuery
from data.logger import logger
from data import aiogram_bot
from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from states.states import AddTgAccState, AddAccsArchive
from data.config_telethon_scheme import AuthTelethon
from database import db, accs_action
from telethon import errors
from filters.known_user import KnownUser
from filters.is_admin import IsAdmin
from utils import check_session
import zipfile
import rarfile

router = Router()
router.message.filter(
    IsAdmin(F)
)


async def acc_in_table(phone):
    accounts = await accs_action.db_get_all_tg_accounts()
    if phone in accounts:
        return True
    return False


async def extract_archive(archive_path, extract_path='data/sessions_new'):
    try:
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            print(f'Zip-архив {archive_path.split("/")[-1]} распакован')
        elif archive_path.endswith('.rar'):
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(extract_path)
            print(f'Rar-архив {archive_path.split("/")[-1]} распакован')
        else:
            print(f'Не поддерживаемый формат архива: {archive_path}')
            return False

        return True
    except Exception as e:
        print(f"Ошибка при распаковке архива: {e}")
        return False
    finally:
        await upload_accs_to_db()


async def upload_accs_to_db(path='data/sessions_new'):
    try:
        sessions = []
        accounts = await accs_action.db_get_all_tg_accounts()
        for filename in os.listdir(path):
            if filename.endswith('.session') and filename not in accounts:
                sessions.append(filename.rstrip('.session'))

        for sess in sessions:
            if await check_session(sess):
                await accs_action.db_add_tg_account(sess)
                await aiogram_bot.send_message(462813109, f'Аккаунт {sess} загружен в базу данных')
            else:
                await aiogram_bot.send_message(462813109, f'Ошибка авторизации {sess}. Аккаунт не загружен.')
    except Exception as e:
        logger.error(e)
        await aiogram_bot.send_message(462813109, f'Ошибка при загрузке аккаунтов')



@router.callback_query(F.data == 'tg_accs_add', KnownUser())
async def input_phone(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    logger.info('awaiting phone to add telegram account')
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите номер телефона: ', reply_markup=kb_admin.tg_back())
    await state.set_state(AddTgAccState.input_2fa)


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
            await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=kb_admin.tg_accs_btns())
        await state.set_state(AddTgAccState.input_code)
    else:
        logger.error(f'account with phone {phone} already exists in db')
        await message.answer(f'Аккаунт с номером {phone} уже существует в базе данных.')
        await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=kb_admin.tg_accs_btns())


@router.message(StateFilter(AddTgAccState.input_code))
async def add_tg_acc(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        password = data['password']
        await data['tg_client'].login_process_code(message.text)
        await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
        await message.answer('Настройки телеграм аккаунтов:', reply_markup=kb_admin.tg_accs_btns())
        await accs_action.db_add_tg_account(data['phone'])
        logger.info('telegram account successfully added to db')

    except errors.SessionPasswordNeededError as e:
        try:
            logger.error(e)
            login = await data['tg_client'].login_process_code(password=password)
            if login:
                await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
                await message.answer('Настройки телеграм аккаунтов:', reply_markup=kb_admin.tg_accs_btns())
                await accs_action.db_add_tg_account(data['phone'])
                logger.info('telegram account successfully added to db')
            else:
                await message.answer('Ошибка логина. Попробуйте еще раз.')
        except Exception as e:
            logger.error(e)
            await message.answer('Ошибка логина. Пожалуйста, попробуйте еще раз.')
            return

    await state.clear()


@router.message(Command('upload_archive'), IsAdmin(F))
async def process_upload_archive(message: Message, state: FSMContext):
    await message.answer('Ожидаю архив с аккаунтами: ')
    await state.set_state(AddAccsArchive.input_archive)


@router.message(AddAccsArchive.input_archive)
async def proceed_archive(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_name = message.document.file_name
    print(file_name)
    file = await aiogram_bot.get_file(file_id)
    file_path = file.file_path

    archive_path = f'archives/{file_name}'
    await aiogram_bot.download_file(file_path, archive_path)
    await message.answer(f'Архив {file_name} загружен.')
    await state.clear()
    await asyncio.sleep(5)
    await extract_archive(archive_path)
