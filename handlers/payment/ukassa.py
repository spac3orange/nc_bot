from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from keyboards import kb_admin
from data import aiogram_bot, payment_config
from aiogram.types.message import ContentType
from states.states import UkassaPayment
from database import payment_action
router = Router()

#prices = {'1_month': 250*100, '3_month': 450*100, '6_month': 750*100, '12_month': 1140*100}

@router.message(UkassaPayment.input_sum, lambda message: message.text.isdigit() and int(message.text) >= 300)
async def buy_ukassa(message: Message, bot: aiogram_bot, state: FSMContext):
    payment_sum = message.text
    price = LabeledPrice(label=f'Пополнение баланса {payment_sum}р', amount=int(payment_sum)*100)
    photo = 'https://i.postimg.cc/QVGjvsJr/cb-bot.jpg'
    if payment_config.ukassa_token.split(':')[1] == 'TEST':
        await message.answer('Тестовый режим оплаты')

    await bot.send_invoice(chat_id=message.from_user.id,
                           title='Пополнение баланса',
                           description='Пополнение баланса CommentBoost_Bot',
                           provider_token=payment_config.ukassa_token,
                           currency='rub',
                           photo_url=photo,
                           photo_width=416,
                           photo_height=416,
                           photo_size=416,
                           is_flexible=False,
                           prices=[price],
                           start_parameter='one-month-subscription',
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




