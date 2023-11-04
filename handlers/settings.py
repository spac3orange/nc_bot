from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import settings_btns
from filters.is_admin import IsAdmin
from database.db_action import db_get_all_data
from filters.known_user import KnownUser
router = Router()


@router.callback_query(F.data == 'settings', KnownUser())
async def process_start(callback: CallbackQuery):
    #await callback.message.delete()
    all_data = await db_get_all_data()
    telegram_channels = ' '.join([x[0] for x in all_data['telegram_groups']] or 'Нет добавленных каналов')
    telegram_accounts = len(all_data['telegram_accounts'] or 'Нет добавленных аккаунтов')
    gpt_accounts = len(all_data['gpt_accounts']) or 'Нет добавленных аккаунтов'
    monitor = ''.join('Установлен' if all_data['telegram_monitor_account'][0] else 'Не установлен')
    print(all_data)
    await callback.message.answer(text=f'<b>Монитор:</b> {monitor}\n'
                                       f'<b>Telegram аккаунты:</b> {telegram_accounts}\n'
                                       f'<b>Каналы:</b> {telegram_channels}\n'
                                       f'<b>GPT Аккаунты:</b> {gpt_accounts}\n\n'
                                       '<b>Информация:</b> /help_settings',
                                  reply_markup=settings_btns(),
                                  parse_mode='HTML')


@router.callback_query(F.data == 'back_to_settings')
async def back_to_settings(callback: CallbackQuery):
    #await callback.message.delete()
    all_data = await db_get_all_data()
    telegram_channels = ' '.join([x[0] for x in all_data['telegram_groups']])
    telegram_accounts = len(all_data['telegram_accounts']) or 'Нет добавленных аккаунтов'
    gpt_accounts = len(all_data['gpt_accounts']) or 'Нет добавленных аккаунтов'
    monitor = ''.join('Установлен' if all_data['telegram_monitor_account'][0] else 'Не установлен')
    await callback.message.answer(text=f'<b>Монитор:</b> {monitor}\n'
                                       f'<b>Telegram аккаунты:</b> {telegram_accounts}\n'
                                       f'<b>Каналы:</b> {telegram_channels}\n'
                                       f'<b>GPT Аккаунты:</b> {gpt_accounts}\n\n'
                                       '<b>Информация:</b> /help_settings',
                                  reply_markup=settings_btns(),
                                  parse_mode='HTML')