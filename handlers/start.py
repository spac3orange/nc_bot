from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from database import db
from aiogram.fsm.context import FSMContext
from data import logger

router = Router()
router.message.filter(
    KnownUser()
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

@router.message(Command(commands='contacts'))
async def get_monitor_status(message: Message):
    await message.answer(f'Администратор: @Jisiehrk\n')
    logger.info(f'User @{message.from_user.username} get contacts.')

@router.message(CommandStart)
async def process_start(message: Message):
    uid, uname = message.from_user.id, message.from_user.username
    await db.db_add_user(uid, uname)
    if not IsAdmin(F):
        await db.db_add_user_today(uid, uname)
    await db.add_user_to_subscriptions(uid)

    logger.info(f'User @{message.from_user.username} connected. '
                        f'User id: {message.from_user.id}')

    # status = await monitor.get_status()
    # uid = message.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)

    if IsAdmin(F):
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'Мониторинг <b>{"работает 🟢" if user_monitoring_status else "выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('Добро пожаловать!\n\n'
                             f'Мониторинг <b>{"работает 🟢" if user_monitoring_status else "выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')


@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery):
    uid = callback.from_user.id
    user_monitoring_status = await db.get_monitoring_status(uid)

    if IsAdmin(F):
        await callback.message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await callback.message.answer('Добро пожаловать!\n\n'
                             f'Мониторинг <b>{"работает 🟢" if user_monitoring_status else "выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns_admin(),
                             parse_mode='HTML')
    else:
        await callback.message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await callback.message.answer('Добро пожаловать!\n\n'
                             f'Мониторинг <b>{"работает 🟢" if user_monitoring_status else "выключен 🔴"}</b>',
                             reply_markup=kb_admin.start_btns(),
                             parse_mode='HTML')