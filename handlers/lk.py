from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from data import logger
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from pprint import pprint
from database import db, payment_action
from states.states import AddSubscription, BuyAccs
from aiogram.fsm.context import FSMContext

router = Router()
router.message.filter(
)


@router.callback_query(F.data == 'lk')
async def process_lk(callback: CallbackQuery):

    uid = callback.from_user.id
    uname = callback.from_user.username
    user_data = await db.get_user_info(uid)
    ref_link = f'https://t.me/MagicComment24_bot?start=ref{uid}'
    accounts = ''
    commentaries = ''
    if user_data['sub_type'] == 'DEMO':
        accounts = '1 (демо)'
        commentaries = '1'
    elif user_data['sub_type'] == 'Подписка на 1 день':
        accounts = len(await db.get_user_accounts(uid))
        commentaries = '7'
    elif user_data['sub_type'] == 'Подписка на 7 дней':
        accounts = len(await db.get_user_accounts(uid))
        commentaries = '147'
    elif user_data['sub_type'] == 'Подписка на 30 дней':
        accounts = len(await db.get_user_accounts(uid))
        commentaries = '1050'
    sub_start = 'Не активна' if user_data['sub_start_date'] is None else user_data['sub_start_date']
    sub_end = 'Не активна' if user_data['sub_end_date'] is None else user_data['sub_end_date']
    print(sub_start)
    pprint(user_data)
    if user_data:
        await callback.message.answer(f'<b>ID:</b> {uid}\n'
                                      f'<b>Username:</b> @{uname}\n\n'
                                      
                                      f'<b>Баланс:</b> {user_data["balance"]} рублей\n'
                                      f'<b>Уровень подписки:</b> {user_data["sub_type"]}\n'
                                      f'<b>Начало подписки:</b> {sub_start}\n'
                                      f'<b>Подписка истекает:</b> {sub_end}\n'
                                      f'<b>Доступно аккаунтов:</b> {accounts}\n'
                                      f'<b>Лимит комментариев:</b> {commentaries}\n\n'
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
                                  '\n\n<b>Подписка на 1 день - 300р</b>'
                                  '\n<b>Аккаунты:</b> 1 шт.'
                                  '\n<b>Комментарии:</b> 7 шт.'
                                  '\n<b>Стоимость одного комментария:</b> 42.86 р.'
                                  '\n\n<b>Подписка на 7 дней - 1500р</b>'
                                  '\n<b>Аккаунты:</b> 3 шт.'
                                  '\n<b>Комментарии:</b> 147 шт.'
                                  '\n<b>Стоимость одного комментария:</b> 10.20 р.'
                                  '\n\n<b>Подписка на 30 дней - 5000р</b>'
                                  '\n<b>Аккаунты:</b> 5 шт.'
                                  '\n<b>Комментарии:</b> 1050 шт.'
                                  '\n<b>Стоимость одного комментария:</b> 4.76 р.',
                                  parse_mode='HTML', reply_markup=kb_admin.choose_sub_plan())

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
        accounts = 1
        comments = 7
    elif plan == '7':
        sub_price = 1500
        accounts = 3
        comments = 147
    elif plan == '30':
        sub_price = 5000
        accounts = 5
        comments = 1050
    if user_data:
        if user_data['balance'] >= sub_price:
            accs_available = await db.db_get_all_tg_accounts(True)
            if len(accs_available) >= accounts:
                days = 'день' if plan == '1' else 'дней'
                await callback.message.answer('<b>Спасибо за покупку!</b>'
                                              f'\n<b>Подписка активирована на {plan} {days}</b>'
                                              f'\n<b>Аккаунты:</b> {accounts} шт.'
                                              f'\n<b>Комментарии:</b> {comments} шт.'
                                              f'\n\nДля расширенной настройки аккаунтов, триггеров сообщений и промтов ChatGPT,'
                                              f' перейдите в раздел <b>Настройки</b> /settings', parse_mode='HTML')

                await payment_action.update_subscription_info(callback.from_user.id, int(plan))
                await db.create_user_accounts_table(uid)
                await db.move_accounts(uid, accounts)

            else:
                await callback.message.answer('К сожалению, аккаунтов на данный момент нет в наличии.\n'
                                              'Пожалуйста, попробуйте позже.',
                                              parse_mode='HTML')
        else:
            await callback.message.answer('<b>Недостаточно средств для оплаты тарифа.</b>'
                                          '\n\nДля пополнения баланса, введите команду /add_balance',
                                          parse_mode='HTML')

    else:
        await callback.message.answer('Произошла ошибка, попробуйте позже',
                                      reply_markup=kb_admin.lk_btns(),
                                      parse_mode='HTML')


@router.callback_query(F.data == 'users_buy_accs')
async def process_buy_accs(callback: CallbackQuery, state: FSMContext):
    accs_amount = 0
    uid = callback.from_user.id
    user_balance = (await db.get_user_info(uid))['balance']
    await callback.message.answer('1 Telegram аккаунт - <b>200 рублей</b>\n'
                                  f'Доступно аккаунтов для покупки: <b>{accs_amount}</b>\n'
                                  '<b>Сколько аккаунтов вы хотели бы приобрести?</b>\n\n'
                                  'Отменить /cancel', parse_mode='HTML')
    await state.set_state(BuyAccs.input_amount)


@router.message(BuyAccs.input_amount)
async def confirm_buy_accs(message: Message, state: FSMContext):
    uid = message.from_user.id
    if message.text.isdigit():
        accs_amount = int(message.text)
        total_price = accs_amount * 200
        await message.answer(f'Покупка <b>{accs_amount}</b> Telegram аккаунтов за <b>{total_price}</b> рублей', parse_mode='HTML',
                             reply_markup=kb_admin.confirm_buy_accs(accs_amount))
        await state.clear()


@router.callback_query(F.data.startswith('confirm_buy_accs'))
async def update_additional_accs(callback: CallbackQuery):
    uid = callback.from_user.id
    user_balance = (await db.get_user_info(uid))['balance']
    amount = int(callback.data.split('_')[-1])
    if user_balance < amount * 200:
        await callback.message.answer('На вашем балансе не достаточно средств для покупки. Пожалуйста, пополните баланс и попробуйте еще раз.')
        return
