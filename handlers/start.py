from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data import config_aiogram
from data import logger
from database import db
from keyboards import kb_admin
from utils import user_license
from filters.known_user import KnownUser

router = Router()
router.message.filter(
)

license_applied = dict()





@router.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    uid = message.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)
    status = 'Работает 🟢' if user_monitoring_status else 'Выключен 🔴'
    if str(message.from_user.id) in config_aiogram.admin_id:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'Статус: <b>{status}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'Статус: <b>{"Работает 🟢"}</b>',
                             reply_markup=kb_admin.get_history_user(),
                             parse_mode='HTML')
    await state.clear()

@router.message(Command(commands='support'))
async def get_monitor_status(message: Message):
    await message.answer(f'<b>Тех. Поддержка</b>: @mrmagic24\n', parse_mode='HTML')
    logger.info(f'User @{message.from_user.username} get support.')


@router.message(Command(commands='start'))
async def process_license(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    if not license_applied.get(uid):
        await message.answer(text=user_license.license_text, reply_markup=kb_admin.process_license(), parse_mode='HTML')
    else:
        uid, uname = message.from_user.id, message.from_user.username
        license_applied[uid] = True

        await db.db_add_user(uid, uname)
        if uid not in config_aiogram.admin_id:
            await db.db_add_user_today(uid, uname)
        await db.add_user_to_subscriptions(uid)

        logger.info(f'User @{message.from_user.username} connected. '
                    f'User id: {message.from_user.id}')

        user_monitoring_status = await db.get_monitoring_status(uid)

        if str(message.from_user.id) in config_aiogram.admin_id:
            await message.answer(
                                 f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                                 reply_markup=kb_admin.start_btns_admin(),
                                 parse_mode='HTML')
        else:
            await message.answer(
                                 f'Статус: <b>{" Работает 🟢"}</b>',
                                 reply_markup=kb_admin.get_history_user(),
                                 parse_mode='HTML')



@router.callback_query(F.data == 'start_accept_license')
async def process_start(callback: CallbackQuery):
    uid, uname = callback.from_user.id, callback.from_user.username
    license_applied[uid] = True

    await db.db_add_user(uid, uname)
    if uid not in config_aiogram.admin_id:
        await db.db_add_user_today(uid, uname)
    await db.add_user_to_subscriptions(uid)

    logger.info(f'User @{callback.from_user.username} connected. '
                        f'User id: {callback.from_user.id}')

    user_monitoring_status = await db.get_monitoring_status(uid)

    if str(callback.from_user.id) in config_aiogram.admin_id:
        await callback.message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await callback.message.answer('Добро пожаловать!\n\n'
                             f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await callback.message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await callback.message.answer('Добро пожаловать!\n\n'
                             f'Статус: <b>{" Работает 🟢"}</b>',
                             reply_markup=kb_admin.get_history_user(),
                             parse_mode='HTML')


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)
    await state.clear()
    if str(callback.from_user.id) in config_aiogram.admin_id:
        await callback.message.answer(
                             f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await callback.message.answer(
                             f'Статус: <b>{" Работает 🟢"}</b>',
                             reply_markup=kb_admin.get_history_user(),
                             parse_mode='HTML')



@router.message()
async def unknown_message(message: Message):
    await message.answer('Я не знаю такой команды😬')