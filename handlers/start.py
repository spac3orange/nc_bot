from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from database import db
from aiogram.fsm.context import FSMContext
from data import logger
from utils import user_license
from data import config_aiogram
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
                             f'Статус: <b>{status}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')
    await state.clear()

@router.message(Command(commands='contacts'))
async def get_monitor_status(message: Message):
    await message.answer(f'Администратор: @Jisiehrk\n')
    logger.info(f'User @{message.from_user.username} get contacts.')


@router.message(CommandStart)
async def process_license(message: Message):
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
                                 f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                                 reply_markup=kb_admin.start_btns(),
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
                             f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery):
    uid = callback.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)

    if str(callback.from_user.id) in config_aiogram.admin_id:
        await callback.message.answer(
                             f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await callback.message.answer(
                             f'Статус: <b>{" Работает 🟢" if user_monitoring_status else "Выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')