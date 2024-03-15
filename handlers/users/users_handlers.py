from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from database import db, accs_action
from pprint import pprint
from states.states import UsersAddState
from aiogram.fsm.context import FSMContext
from data.logger import logger
router = Router()
router.message.filter(
    IsAdmin(F)
)

@router.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    uid = message.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)
    status = 'Работает 🟢' if user_monitoring_status else 'Выключен 🔴'
    if IsAdmin(F):
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'<b>{status}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'<b>{status}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')
    await state.clear()

@router.callback_query(F.data == 'users_settings', IsAdmin(F))
async def process_users_settings(callback: CallbackQuery):
    await callback.answer()
    users = await db.db_get_users()
    users_list = []
    for uid, name, mon, notif in users:
        user = []
        user_data = await db.get_user_info(uid)
        print(user_data)
        accounts = len(await accs_action.get_user_accounts(uid)) or '0'
        channels = '\n'.join(await db.db_get_all_telegram_channels(uid))
        user.append(f'\n<b>Ник</b>: @{name}\n'
                          f'<b>ID:</b> {uid}\n'
                          f'<b>Баланс:</b> {user_data["balance"]}\n'
                          f'<b>Уровень подписки:</b> {user_data["sub_type"]}\n'
                          f'<b>Начало подписки:</b> {user_data["sub_start_date"]}\n'
                          f'<b>Подписка истекает:</b> {user_data["sub_end_date"]}\n'
                          f'<b>Аккаунтов:</b> {accounts}\n'
                          f'<b>Приглашенных пользователей:</b> 0\n'
                          f'<b>Бонусные дни подписки:</b> 0\n'
                          f'<b>Отправлено комментариев:</b> {user_data["comments_sent"]}\n'
                          f'<b>Каналы:</b> {channels}\n'
                          f'<b>Мониторинг:</b> {"🟢" if mon else "🔴"}')
        user = '\n'.join(user)
        await callback.message.answer(text=user, parse_mode='HTML')

    pprint(users_list)
    users_list_str = '\n'.join(users_list)
    pprint(users_list_str)
    await callback.message.answer(text='<b>Панель управления пользователями</b>\n\n',
                                  reply_markup=kb_admin.users_settings_btns(), parse_mode='HTML')

@router.callback_query(F.data == 'back_to_users_settings')
async def back_to_users_settings(callback: CallbackQuery):
    await callback.answer()
    users = await db.db_get_users()
    users_list = []
    for uid, name, mon, notif in users:
        user = []
        user_data = await db.get_user_info(uid)
        accounts = len(await accs_action.get_user_accounts(uid)) or '0'
        channels = '\n'.join(await db.db_get_all_telegram_channels(uid))
        user.append(f'\n<b>Ник</b>: @{name}\n'
                    f'<b>ID:</b> {uid}\n'
                    f'<b>Баланс:</b> {user_data["balance"]}\n'
                    f'<b>Уровень подписки:</b> {user_data["sub_type"]}\n'
                    f'<b>Начало подписки:</b> {user_data["sub_start_date"]}\n'
                    f'<b>Подписка истекает:</b> {user_data["sub_end_date"]}\n'
                    f'<b>Аккаунтов:</b> {accounts}\n'
                    f'<b>Приглашенных пользователей:</b> 0\n'
                    f'<b>Бонусные дни подписки:</b> 0\n'
                    f'<b>Отправлено комментариев:</b> {user_data["comments_sent"]}\n'
                    f'<b>Каналы:</b> {channels}\n'
                    f'<b>Мониторинг:</b> {"🟢" if mon else "🔴"}')
        user = '\n'.join(user)
        await callback.message.answer(text=user, parse_mode='HTML')


@router.callback_query(F.data == 'users_settings')
async def inv_users_settings(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Извините, функция доступна только администратору.')

@router.callback_query(F.data == 'users_add')
async def process_users_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите id и ник пользователя без символа "@" через запятую: ')
    await state.set_state(UsersAddState.input_creds)

@router.message(UsersAddState.input_creds)
async def user_add_to_db(message: Message, state: FSMContext):
    try:
        uid, name = [x.strip() for x in message.text.split(',')]

        await db.db_add_user(int(uid), name)
        logger.info(f'User {name} added to database')
        await message.answer(f'Пользователь {name} добавлен в базу данных.')
        await state.clear()
    except Exception as e:
        logger.error(e)
        await message.answer(f'Ошибка при добавлении пользователя\nОтменить /cancel')


@router.callback_query(F.data == 'users_del')
async def process_users_del(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    users = await db.db_get_users()
    users_list = []
    for user in users:
        name = user[1]
        users_list.append(name)
    await callback.message.answer('Выберите пользователя для удаления: ',
                                  reply_markup=kb_admin.users_names_btns(users_list))

@router.callback_query(F.data.startswith('users_del_'))
async def delete_from_db(callback: CallbackQuery):
    await callback.answer()
    user_name = callback.data.split('_')[-1].strip()

    await db.db_delete_user(user_name)
    await callback.message.answer(f'Пользователь <b>{user_name}</b> удален из базы данных.', parse_mode='HTML',
                                  reply_markup=kb_admin.users_settings_btns())