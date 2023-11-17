from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
from filters.known_user import KnownUser
from filters.sub_types import BasicSub
from aiogram.fsm.context import FSMContext
from states.states import EditAccInfo
from data.config_telethon_scheme import AuthTelethon
from database import db
router = Router()
router.message.filter(
    KnownUser()
)




@router.callback_query(F.data == 'user_tg_accs_settings', ~BasicSub())
async def tg_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('<b>Настройки телеграм аккаунтов</b>\n\n'
                                  'Здесь можно настроить инфо аккаунта, такое как:\n'
                                  '<b>Имя, Фамилия, Bio, Аватар</b>\n\n'
                                  'Информация: /help_accs', reply_markup=kb_admin.users_tg_accs_btns(),
                                  parse_mode='HTML')

@router.callback_query(F.data == 'choose_acc_user')
async def choose_acc_user(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    operation = 'change_info'
    accounts = await db.get_user_accounts(uid)
    await callback.message.answer('Выберите аккаунт:', reply_markup=kb_admin.generate_accs_keyboard_users(accounts,
                                                                                                     operation))

@router.callback_query(F.data.startswith('account_change_info_'))
async def change_info_menu(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    account = callback.data.split('_')[-1]
    print(account)
    await callback.message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                                  parse_mode='HTML')

@router.callback_query(F.data.startswith('acc_edit_name_'))
async def acc_change_name(callback: CallbackQuery, state: FSMContext):
    account = callback.data.split('_')[-1]
    await callback.message.answer('Введите новое имя:')
    await state.set_state(EditAccInfo.change_name)
    await state.update_data(account=account)

@router.message(EditAccInfo.change_name)
async def name_changed(message: Message, state: FSMContext):
    account = (await state.get_data())['account']
    session = AuthTelethon(account)
    res = await session.change_first_name(message.text)
    if res:
        await message.answer('Имя изменено')
    else:
        await message.answer('Произошла ошибка, попробуйте позже')
    await state.clear()












@router.callback_query(F.data == 'back_to_users_accs')
async def back_to_accs(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Настройки телеграм аккаунтов:', reply_markup=kb_admin.users_tg_accs_btns())
    await state.clear()

@router.callback_query(F.data == 'user_tg_accs_settings')
async def tg_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('Извините, этот раздел не доступен для пользователей с бесплатной подпиской')