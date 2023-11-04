from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import settings_btns, users_settings_btns, users_names_btns
from filters.is_admin import IsAdmin
from database.db_action import db_get_all_data, db_get_users, db_add_user, db_delete_user
from pprint import pprint
from states.states import UsersAddState, UsersDelState
from aiogram.fsm.context import FSMContext
from data.logger import logger
router = Router()


@router.callback_query(F.data == 'users_settings', IsAdmin(F))
async def process_users_settings(callback: CallbackQuery):
    users = await db_get_users()
    users_list = []
    for uid, name in users:
        users_list.append(f'\n<b>Ник</b>: {name}\n<b>ID: {uid}</b>')
    pprint(users_list)
    users_list_str = '\n'.join(users_list)
    pprint(users_list_str)
    await callback.message.answer(text=users_list_str, reply_markup=users_settings_btns(), parse_mode='HTML')

@router.callback_query(F.data == 'back_to_users_settings')
async def back_to_users_settings(callback: CallbackQuery):
    users = await db_get_users()
    users_list = []
    for uid, name in users:
        users_list.append(f'\n<b>Ник</b>: {name}\n<b>ID: {uid}</b>')
    pprint(users_list)
    users_list_str = '\n'.join(users_list)
    pprint(users_list_str)
    await callback.message.answer(text=users_list_str, reply_markup=users_settings_btns(), parse_mode='HTML')


@router.callback_query(F.data == 'users_settings')
async def inv_users_settings(callback: CallbackQuery):
    await callback.message.answer('Извините, функция доступна только администратору.')

@router.callback_query(F.data == 'users_add')
async def process_users_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите id и ник пользователя без символа "@" через запятую: ')
    await state.set_state(UsersAddState.input_creds)

@router.message(UsersAddState.input_creds)
async def user_add_to_db(message: Message, state: FSMContext):
    try:
        uid, name = [x.strip() for x in message.text.split(',')]

        await db_add_user(int(uid), name)
        logger.info(f'User {name} added to database')
        await message.answer(f'Пользователь {name} добавлен в базу данных.')
        await state.clear()
    except Exception as e:
        logger.error(e)
        await message.answer(f'Ошибка при добавлении пользователя')


@router.callback_query(F.data == 'users_del')
async def process_users_del(callback: CallbackQuery, state: FSMContext):
    users = await db_get_users()
    users_list = []
    for user in users:
        name = user[1]
        users_list.append(name)
    await callback.message.answer('Выберите пользователя для удаления: ',
                                  reply_markup=users_names_btns(users_list))

@router.callback_query(F.data.startswith('users_del_'))
async def delete_from_db(callback: CallbackQuery):
    user_name = callback.data.split('_')[-1].strip()

    await db_delete_user(user_name)
    await callback.message.answer(f'Пользователь <b>{user_name}</b> удален из базы данных.', parse_mode='HTML',
                                  reply_markup=users_settings_btns())