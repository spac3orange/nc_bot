from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from database import db
from pprint import pprint
from states.states import UsersAddState
from aiogram.fsm.context import FSMContext
from data.logger import logger
from states.states import PromoteUser
router = Router()
router.message.filter(
    IsAdmin(F)
)



@router.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    if IsAdmin(F):
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'<b>{"Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'<b>{"Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')
    await state.clear()

@router.callback_query(F.data == 'promote_user')
async def promote_user(callback: CallbackQuery, state: FSMContext):
    users = await db.db_get_users()
    operation = 'promote'
    users_list = []
    for uid, uname, mon, notif in users:
        users_list.append(uname)
    print(users)
    await callback.message.answer('Выберите пользователя для повышения прав:',
                                  reply_markup=kb_admin.generate_users_promote(users_list, operation))


@router.callback_query(F.data.startswith('users_promote__'))
async def name_for_promote(callback: CallbackQuery, state: FSMContext):
    user_name = callback.data.split('__')[-1]
    user_id = await db.get_user_id_by_username(user_name)
    user_info = await db.get_user_info(user_id)
    user_status = user_info['sub_type']
    await state.update_data(user_name=user_name, user_id=user_id)
    await callback.message.answer(f'Выбран пользователь <b>{user_name}</b>\n'
                                  f'Уровень подписки: <b>{user_status}</b>\n\n'
                                  f'Введите новый уровень подписки для пользователя:\n\n'
                                  f'1. DEMO\n'
                                  f'2. Серебряный\n'
                                  f'3. Золотой\n'
                                  f'4. VIP\n'
                                  f'5. Admin', parse_mode='HTML')
    await state.set_state(PromoteUser.input_promote)


@router.message(PromoteUser.input_promote)
async def apply_promote(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if message.text == '1':
        user_status = 'DEMO'
    elif message.text == '2':
        user_status = 'Серебряный'
    elif message.text == '3':
        user_status = 'Золотой'
    elif message.text == '4':
        user_status = 'VIP'
    elif message.text == '5':
        user_status = 'Admin'
    else:
        user_status = None
        await message.answer('Неверный ввод, попробуйте еще раз.\n\n'
                             'Отмена /cancel')

    if user_status:
        if user_status == 'DEMO':
            await db.return_accounts(state_data['user_id'])
            await db.update_subscription_type(state_data['user_id'], user_status)
            await message.answer(
                f'Пользователь {state_data["user_name"]} успешно повышен до уровня: <b>{user_status}</b>',
                reply_markup=kb_admin.users_settings_btns(), parse_mode='HTML')
        else:
            await db.create_user_accounts_table(state_data['user_id'])
            await db.update_subscription_type(state_data['user_id'], user_status)
            await message.answer(f'Пользователь {state_data["user_name"]} успешно повышен до уровня: <b>{user_status}</b>',
                                 reply_markup=kb_admin.users_settings_btns(), parse_mode='HTML')
        await state.clear()
