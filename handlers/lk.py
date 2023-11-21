from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from data import logger
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from pprint import pprint
from database import db

router = Router()
router.message.filter(
    KnownUser()
)


@router.callback_query(F.data == 'lk')
async def process_admin_panel(callback: CallbackQuery):

    uid = callback.from_user.id
    uname = callback.from_user.username
    user_data = await db.get_user_info(uid)
    ref_link = f'https://t.me/neuro_comm_bot?start=ref{uid}'
    accounts = len(await db.get_user_accounts(uid)) or '1'
    pprint(user_data)
    if user_data:
        await callback.message.answer(f'<b>ID:</b> {uid}\n'
                                      f'<b>Username:</b> @{uname}\n\n'
                                      
                                      f'<b>Баланс:</b> {user_data["balance"]}\n'
                                      f'<b>Уровень подписки:</b> {user_data["sub_type"]}\n'
                                      f'<b>Начало подписки:</b> {user_data["sub_start_date"]}\n'
                                      f'<b>Подписка истекает:</b> {user_data["sub_end_date"]}\n'
                                      f'<b>Доступно аккаунтов:</b> {accounts}\n\n'
                                      f'<b>Статистика:\n</b>'
                                      f'Отправлено комментариев: {user_data["comments_sent"]}\n\n'
                                      f'<b>Реферальная программа:</b>\n'
                                      f'Приглашенных пользователей: 0\n'
                                      f'Бонусные дни подписки: 0\n\n'
                                      f'<b>Реферальная ссылка:</b> \n{ref_link}\n\n',
                                      reply_markup=kb_admin.lk_btns(),
                                      parse_mode='HTML')
    else:
        await callback.message.answer('Произошла ошибка, попробуйте позже',
                                      reply_markup=kb_admin.lk_btns(),
                                      parse_mode='HTML')


@router.callback_query(F.data == 'subscribe')
async def process_subscribe(callback: CallbackQuery):
    await callback.message.answer('В разработке.')

@router.callback_query(F.data == 'add_balance')
async def process_add_balance(callback: CallbackQuery):
    await callback.message.answer('В разработке.')