import asyncio
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram import Router, F
from keyboards import kb_admin
from filters.sub_types import BasicSub
from aiogram.fsm.context import FSMContext
from states.states import EditAccInfo, UserSendPhoto
from data.config_telethon_scheme import TelethonConnect, TelethonSendMessages
from database import db, accs_action
from typing import List, Tuple
from data import logger, aiogram_bot
import random
router = Router()
router.message.filter(
)


async def get_info(accounts: list, uid=None) -> List[Tuple[str]]:
    accs_info = []
    for session in accounts:
        try:
            slp = random.randint(3, 5)
            await asyncio.sleep(slp)
            sess = TelethonConnect(session)
            info = await sess.get_info(uid)
            if info:
                accs_info.append(info)
            else:
                try:
                    await aiogram_bot.send_message(int(uid), f'Аккаунт {session} заблокирован.')
                    continue
                except Exception as e:
                    logger.error(e)
        except Exception as e:
            print(e)
    return accs_info


@router.callback_query(F.data == 'user_tg_accs_settings', ~BasicSub())
async def tg_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('<b>Настройки телеграм аккаунтов</b>\n\n'
                                  'Здесь можно настроить инфо аккаунта, такое как:\n'
                                  '<b>Имя, Фамилия, Пол, Bio, Аватар, Username</b>\n\n'
                                  'ВНИМАНИЕ! Мы настоятельно НЕ рекомендуем злоупотреблять данной функцией и изменять инфорамцию аккаунта чаще одного раза в день!\n'
                                  'С высокой вероятностью это может привести к блокировке вашего аккаунта.',
                                  reply_markup=kb_admin.users_tg_accs_btns(),
                                  parse_mode='HTML')

@router.callback_query(F.data == 'choose_acc_user')
async def choose_acc_user(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    operation = 'change_info'
    accounts = await accs_action.get_user_accounts(uid)
    await callback.message.answer('<b>Выберите аккаунт:</b>',
                                  reply_markup=kb_admin.generate_accs_keyboard_users(accounts, operation),
                                  parse_mode='HTML')

@router.callback_query(F.data.startswith('account_change_info_'))
async def change_info_menu(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    account = callback.data.split('_')[-1]
    print(account)
    await callback.message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                                  parse_mode='HTML')


# username
@router.callback_query(F.data.startswith('acc_edit_username_'))
async def acc_change_username(callback: CallbackQuery, state: FSMContext):
    account = callback.data.split('_')[-1]
    await callback.message.answer('Введите новый Username:')
    await state.set_state(EditAccInfo.change_username)
    await state.update_data(account=account)

@router.message(EditAccInfo.change_username)
async def name_changed(message: Message, state: FSMContext):
    account = (await state.get_data())['account']
    session = TelethonSendMessages(account)
    res = await session.change_username(message.text)
    if res == 'username_taken':
        await message.answer('Username занят, попробуйте еще раз')
        return
    elif res == 'done':
        await message.answer('Username изменен 👍')
        await message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                             parse_mode='HTML')
    else:
        await message.answer('Произошла ошибка, попробуйте позже')
    await state.clear()


# name
@router.callback_query(F.data.startswith('acc_edit_name_'))
async def acc_change_name(callback: CallbackQuery, state: FSMContext):
    account = callback.data.split('_')[-1]
    await callback.message.answer('Введите новое имя:')
    await state.set_state(EditAccInfo.change_name)
    await state.update_data(account=account)

@router.message(EditAccInfo.change_name)
async def name_changed(message: Message, state: FSMContext):
    account = (await state.get_data())['account']
    session = TelethonSendMessages(account)
    res = await session.change_first_name(message.text)
    if res:
        await message.answer('Имя изменено 👍')
        await message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                             parse_mode='HTML')
    else:
        await message.answer('Произошла ошибка, попробуйте позже')
    await state.clear()


# surname
@router.callback_query(F.data.startswith('acc_edit_surname_'))
async def acc_edit_surname(callback: CallbackQuery, state: FSMContext):
    account = callback.data.split('_')[-1]
    await callback.message.answer('Введите новую фамилию:')
    await state.set_state(EditAccInfo.change_surname)
    await state.update_data(account=account)


@router.message(EditAccInfo.change_surname)
async def name_changed(message: Message, state: FSMContext):
    account = (await state.get_data())['account']
    session = TelethonSendMessages(account)
    res = await session.change_last_name(message.text)
    if res:
        await message.answer('Фамилия изменена 👍')
        await message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                             parse_mode='HTML')
    else:
        await message.answer('Произошла ошибка, попробуйте позже')
    await state.clear()


# bio
@router.callback_query(F.data.startswith('acc_edit_bio_'))
async def acc_edit_bio(callback: CallbackQuery, state: FSMContext):
    account = callback.data.split('_')[-1]
    await callback.message.answer('Введите новую информацию для размещения в био:')
    await state.set_state(EditAccInfo.change_bio)
    await state.update_data(account=account)


@router.message(EditAccInfo.change_bio)
async def name_changed(message: Message, state: FSMContext):
    account = (await state.get_data())['account']
    session = TelethonSendMessages(account)
    res = await session.change_bio(message.text)
    if res:
        await message.answer('Био изменено 👍')
        await message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                             parse_mode='HTML')
    else:
        await message.answer('Произошла ошибка, попробуйте позже')
    await state.clear()


@router.callback_query(F.data == 'users_accs_get_info')
async def user_accs_get_info(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Запрашиваю информацию о подключенных аккаунтах...⏳')
    uid = callback.from_user.id
    try:
        accounts = await accs_action.get_user_accounts(uid)
        displayed_accounts = '\n'.join(accounts)
        if accounts:
            accs_info = await get_info(accounts, uid)
            await callback.message.answer(f'<b>Аккануты:</b>\n{displayed_accounts}', parse_mode='HTML')
            for phone, id, name, surname, username, restricted, about, sex in accs_info:
                string = ''
                string += (
                    f'<b>Тел:</b> {phone}'
                    f'\n<b>ID:</b> {id}'
                    f'\n<b>Имя:</b> {name}'
                    f'\n<b>Фамилия:</b> {surname}'
                    f'\n<b>Пол:</b> {sex}'
                    f'\n<b>Ник:</b> @{username}'
                    f'\n<b>Био:</b> {about}'
                    f'\n<b>Ограничения:</b> {restricted}')
                await callback.message.answer(text=string, parse_mode='HTML')
            await back_to_accs(callback, state)
        else:
            await callback.message.answer('Нет подключенных аккаунтов.')
    except Exception as e:
        logger.error(e)


@router.callback_query(F.data.startswith('acc_edit_avatar_'))
async def acc_edit_avatar(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserSendPhoto.input_photo)
    account = callback.data.split('_')[-1]
    await state.update_data(account=account)
    print(account)
    await callback.message.answer('Отправьте фото для установки аватара'
                                  '\nРазмер фото должен быть менее 20 мегабайт.')

@router.message(F.content_type == ContentType.PHOTO, UserSendPhoto.input_photo)
async def process_photo(message: Message, state: FSMContext):
    uid = message.from_user.id
    state_data = await state.get_data()
    print(state_data)
    account = state_data['account']
    session = TelethonSendMessages(account)
    try:
        randint = random.randint(1000, 9999)
        photo_name = f'{uid}_{randint}_avatar.jpg'
        file_info = await aiogram_bot.get_file(message.photo[-1].file_id)
        downloaded_file = await aiogram_bot.download_file(file_info.file_path)
        with open(photo_name, 'wb') as photo:
            photo.write(downloaded_file.read())
        res = await session.change_profile_photo(photo_name)
        if res:
            await message.answer('Аватар изменен 👍')
            await message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                                 parse_mode='HTML')
        else:
            await message.answer('Произошла ошибка, попробуйте позже')
        await state.clear()
    except Exception as e:
        logger.error(e)
        await message.answer('Произошла ошибка, попробуйте позже')
        await state.clear()




@router.callback_query(F.data == 'back_to_users_accs')
async def back_to_accs(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('<b>Настройки телеграм аккаунтов</b>\n\n'
                                  'Здесь можно настроить инфо аккаунта, такое как:\n'
                                  '<b>Имя, Фамилия, Пол, Bio, Аватар, Username</b>\n\n',
                                  reply_markup=kb_admin.users_tg_accs_btns(),
                                  parse_mode='HTML')
    await state.clear()

@router.callback_query(F.data == 'user_tg_accs_settings')
async def tg_accs_settings(callback: CallbackQuery):
    #await callback.message.delete()
    await callback.message.answer('Извините, этот раздел не доступен для пользователей с бесплатной подпиской')

@router.callback_query(F.data.startswith('acc_edit_sex_'))
async def process_acc_edit_sex(callback: CallbackQuery):
    uid = callback.from_user.id
    account = callback.data.split('_')[-1]
    acc_sex = await accs_action.get_sex_by_phone(account, uid)
    await callback.message.answer(f'<b>Текущий пол</b>: {acc_sex}', parse_mode='HTML')
    await callback.message.answer('Выберите новый пол: ', reply_markup=kb_admin.change_acc_sex(account))

@router.callback_query(F.data.startswith('change_sex_male_'))
async def change_sex_to_male(callback: CallbackQuery):
    uid = callback.from_user.id
    account = callback.data.split('_')[-1]
    await accs_action.update_user_account_sex(uid, account, 'Мужской')
    await callback.message.answer(f'Пол аккаунта {account} изменен на <b>Мужской</b>', parse_mode='HTML')
    await callback.message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                                  parse_mode='HTML')

@router.callback_query(F.data.startswith('change_sex_female_'))
async def change_sex_to_female(callback: CallbackQuery):
    uid = callback.from_user.id
    account = callback.data.split('_')[-1]
    await accs_action.update_user_account_sex(uid, account, 'Женский')
    await callback.message.answer(f'Пол аккаунта {account} изменен на <b>Женский</b>', parse_mode='HTML')
    await callback.message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                                  parse_mode='HTML')

@router.callback_query(F.data.startswith('acc_clear_avatars_'))
async def process_clear_avatars(callback: CallbackQuery):
    uid = callback.from_user.id
    account = callback.data.split('_')[-1]
    session = TelethonSendMessages(account)
    mess = await callback.message.answer('Очищаю аватары...⏳')
    await session.delete_all_profile_photos()
    await mess.edit_text('Аватары удалены 👍')
    await callback.message.answer('<b>Что вы хотите изменить?</b>', reply_markup=kb_admin.edit_acc_info(account),
                                  parse_mode='HTML')

