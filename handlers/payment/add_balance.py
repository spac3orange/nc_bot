from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from data import logger
from keyboards import kb_admin
from database import db
from states.states import UkassaPayment
router = Router()

@router.callback_query(F.data == 'add_balance')
async def process_add_balance(callback: CallbackQuery):
    await callback.message.answer('Выберите способ пополнения счета:', reply_markup=kb_admin.choose_payment_type())

@router.callback_query(F.data == 'payment_cryptomus')
async def process_payment_cryptomus(callback: CallbackQuery):
    await callback.message.answer('В разработке')

@router.callback_query(F.data == 'payment_ukassa')
async def process_payment_ukassa(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите сумму пополнения:'
                                  '\nМинимальная сумма - <b>300р</b> рублей', parse_mode='HTML')
    await state.set_state(UkassaPayment.input_sum)

