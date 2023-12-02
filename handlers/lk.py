from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from data import logger
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from pprint import pprint
from database import db, payment_action
from states.states import AddSubscription
from aiogram.fsm.context import FSMContext

router = Router()
router.message.filter(
)


@router.callback_query(F.data == 'lk')
async def process_admin_panel(callback: CallbackQuery):

    uid = callback.from_user.id
    uname = callback.from_user.username
    user_data = await db.get_user_info(uid)
    ref_link = f'https://t.me/MagicComment24_bot?start=ref{uid}'
    accounts = '10' if user_data['sub_status'] else '1'
    sub_start = 'Не активна' if user_data['sub_start_date'] is None else user_data['sub_start_date']
    sub_end = 'Не активна' if user_data['sub_start_date'] is None else user_data['sub_start_date']
    print(sub_start)
    pprint(user_data)
    if user_data:
        await callback.message.answer(f'<b>ID:</b> {uid}\n'
                                      f'<b>Username:</b> @{uname}\n\n'
                                      
                                      f'<b>Баланс:</b> {user_data["balance"]} рублей\n'
                                      f'<b>Уровень подписки:</b> {user_data["sub_type"]}\n'
                                      f'<b>Начало подписки:</b> {sub_start}\n'
                                      f'<b>Подписка истекает:</b> {sub_end}\n'
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
    await callback.message.answer('<b>Пожалуйста, выберите тариф:</b>'
                                  '\n\n<b>Подписка на 1 день</b>'
                                  '\n<b>Цена:</b> 300 рублей'
                                  '\n<b>Аккаунты:</b> 10 шт.'
                                  '\n<b>Комментарии:</b> 70 шт.'
                                  '\n\n<b>Подписка на 7 дней - 1500р</b>'
                                  '\n<b>Аккаунты:</b> 10 шт.'
                                  '\n<b>Комментарии:</b> 700 шт.'
                                  '\n\n<b>Подписка на 30 дней - 5000р</b>'
                                  '\n<b>Аккаунты:</b> 10 шт.'
                                  '\n<b>Комментарии:</b> 3000 шт.', parse_mode='HTML', reply_markup=kb_admin.choose_sub_plan())

@router.callback_query(F.data.startswith('sub_plan_'))
async def process_sub_plan(callback: CallbackQuery, state: FSMContext):
    plan = callback.data.split('_')[-1]
    days = 'день' if plan == '1' else 'дней'
    await callback.message.answer(f'Выбран тариф: <b>Подписка на {plan} {days}</b>', reply_markup=kb_admin.approve_sub_plan(plan),
                                  parse_mode='HTML')


@router.callback_query(F.data.startswith('approve_sub_plan_'))
async def process_approve_sub_plan(callback: CallbackQuery):
    uid = callback.from_user.id
    uname = callback.from_user.username
    user_data = await db.get_user_info(uid)
    plan = callback.data.split('_')[-1]
    if plan == '1':
        sub_price = 300
    elif plan == '7':
        sub_price = 1500
    elif plan == '30':
        sub_price = 5000
    if user_data:
        if user_data['balance'] >= sub_price:
            days = 'день' if plan == '1' else 'дней'
            await callback.message.answer('Спасибо за покупку!\n'
                                          f'<b>Подписка активирована на {plan} {days}</b>',
                                          parse_mode='HTML')
            await payment_action.update_subscription_info(callback.from_user.id, int(plan))
            await db.create_user_accounts_table(uid)
            ref_link = f'https://t.me/MagicComment24_bot?start=ref{uid}'
            print(user_data['sub_type'])
            accounts = '10' if user_data['sub_status'] else '1'
            pprint(user_data)
            await callback.message.answer(f'<b>ID:</b> {uid}\n'
                                          f'<b>Username:</b> @{uname}\n\n'
    
                                          f'<b>Баланс:</b> {user_data["balance"]} рублей\n'
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
            await callback.answer('Недостаточно средств.'
                                  '\nПожалуйста, пополните баланс')

    else:
        await callback.message.answer('Произошла ошибка, попробуйте позже',
                                      reply_markup=kb_admin.lk_btns(),
                                      parse_mode='HTML')

@router.callback_query(F.data == 'subscribe_prolong')
async def process_sub_prolong(callback: CallbackQuery):
    await callback.message.answer('В разработке.')
