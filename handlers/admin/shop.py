from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from filters.is_admin import IsAdmin
from database import accs_shop_action, accs_action
from states.states import TopAccsShop
from keyboards import kb_admin
from data import logger, aiogram_bot

router = Router()
router.message.filter(
    IsAdmin(F)
)


async def raise_process_admin_shop():
    accs_in_shop = len(await accs_shop_action.db_get_shop_accs())
    basic_accs = len(await accs_action.db_get_all_tg_accounts())
    await aiogram_bot.send_message(f'Аккаунтов в магазине: <b>{accs_in_shop}</b>'
                                   f'\nБесплатных аккаунтов: <b>{basic_accs}</b>',
                                   parse_mode='HTML', reply_markup=kb_admin.accs_shop())


@router.callback_query(F.data == 'admin_shop')
async def process_admin_shop(callback: CallbackQuery):
    await callback.answer()
    accs_in_shop = len(await accs_shop_action.db_get_shop_accs())
    basic_accs = len(await accs_action.db_get_all_tg_accounts())
    await callback.message.answer(f'Аккаунтов в магазине: <b>{accs_in_shop}</b>'
                                  f'\nБесплатных аккаунтов: <b>{basic_accs}</b>',
                                  parse_mode='HTML', reply_markup=kb_admin.accs_shop())


@router.callback_query(F.data == 'refill_shop')
async def process_refill_shop(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('<b>Введите количество аккаунтов для пополнения магазина: </b>'
                                  '\n\nАккаунты будут перенесены из таблицы с беслпатными аккаунтами в таблицу магазина аккаунтов.'
                                  '\n\nОтменить /cancel', parse_mode='HTML')
    await state.set_state(TopAccsShop.input_amount)


@router.message(TopAccsShop.input_amount)
async def confirm_refill_amount(message: Message, state: FSMContext):
    basic_accs = await accs_action.db_get_all_tg_accounts()
    try:
        if message.text.isdigit() and int(message.text) <= len(basic_accs):
            amount = int(message.text)
            shop_updated = await accs_shop_action.transfer_accounts_to_shop(amount)
            if shop_updated:
                await message.answer(f'<b>Магазин обновлен</b>. Добавлено <b>{amount}</b> аккаунтов.', parse_mode='HTML')
            else:
                await message.answer('Ошибка при обновлении магазина.')
            await raise_process_admin_shop()
            await state.clear()
        else:
            await message.answer('Введено не корректное количество аккаунтов. Пожалуйста, попробуйте еще раз.'
                                 '\n\nОтменить /cancel')
            return
    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при обновлении магазина.')
        await state.clear()
