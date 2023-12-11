import asyncio

from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from keyboards import kb_admin
from data import aiogram_bot, payment_config
from aiogram.types.message import ContentType
from states.states import UkassaPayment
from database import payment_action, db
router = Router()

#prices = {'1_month': 250*100, '3_month': 450*100, '6_month': 750*100, '12_month': 1140*100}

@router.message(UkassaPayment.input_sum, lambda message: message.text.isdigit() and int(message.text) >= 300)
async def buy_ukassa(message: Message, bot: aiogram_bot, state: FSMContext):
    payment_sum = message.text
    price = LabeledPrice(label=f'Пополнение баланса {payment_sum}р', amount=int(payment_sum)*100)
    photo = 'https://i.yapx.ru/W2qAP.png'
    await bot.send_invoice(chat_id=message.from_user.id,
                           title='Пополнение баланса',
                           description='Пополнение баланса MagicComment24_bot',
                           provider_token=payment_config.ukassa_token,
                           currency='rub',
                           photo_url=photo,
                           photo_width=480,
                           photo_height=260,
                           photo_size=416,
                           is_flexible=False,
                           prices=[price],
                           start_parameter='balance-top-up',
                           payload='some-invoice-payload')
    await state.clear()

@router.message(UkassaPayment.input_sum)
async def process_inv_sum(message: Message):
    await message.answer('Неверная сумма пополнения!'
                         '\nМинимальная сумма пополнения - <b>300 рублей</b>'
                         '\nОтменить /cancel', parse_mode='HTML')

@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: aiogram_bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, state: FSMContext):
    uid = message.from_user.id
    uname = message.from_user.username
    if message.successful_payment:
        amount = message.successful_payment.total_amount // 100
        await message.answer('Оплата прошла успешно!'
                             f'\nВаш баланс пополнен на <b>{amount}</b> рублей', parse_mode='HTML')
        await payment_action.update_balance(uid, amount)

        await asyncio.sleep(1)
        user_data = await db.get_user_info(uid)
        ref_link = f'https://t.me/MagicComment24_bot?start=ref{uid}'
        accounts = ''
        commentaries = ''
        if user_data['sub_type'] == 'DEMO':
            accounts = '1 (демо)'
            commentaries = '1'
        elif user_data['sub_type'] == 'Подписка на 1 день':
            accounts = '1'
            commentaries = '7'
        elif user_data['sub_type'] == 'Подписка на 7 дней':
            accounts = '3'
            commentaries = '147'
        elif user_data['sub_type'] == 'Подписка на 30 дней':
            accounts = '5'
            commentaries = '1050'
        sub_start = 'Не активна' if user_data['sub_start_date'] is None else user_data['sub_start_date']
        sub_end = 'Не активна' if user_data['sub_end_date'] is None else user_data['sub_start_date']
        if user_data:
            await message.answer(f'<b>ID:</b> {uid}\n'
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
            await message.answer('Произошла ошибка, попробуйте позже',
                                          reply_markup=kb_admin.lk_btns(),
                                          parse_mode='HTML')



