from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards import kb_admin
from states.states import UkassaPayment

router = Router()


@router.message(Command(commands='add_balance'))
async def process_add_balance(message: Message):
    await message.answer('Выберите способ пополнения счета:', reply_markup=kb_admin.choose_payment_type())

@router.callback_query(F.data == 'add_balance')
async def process_add_balance(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Выберите способ пополнения счета:', reply_markup=kb_admin.choose_payment_type())

@router.callback_query(F.data == 'payment_cryptomus')
async def process_payment_cryptomus(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('В разработке')

@router.callback_query(F.data == 'payment_ukassa')
async def process_payment_ukassa(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите сумму пополнения:'
                                  '\nМинимальная сумма - <b>300</b> рублей', parse_mode='HTML')
    await state.set_state(UkassaPayment.input_sum)

