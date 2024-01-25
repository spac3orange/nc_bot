import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from data.logger import logger
from aiogram import Router, F
from keyboards import kb_admin
from aiogram.fsm.context import FSMContext
from states.states import AddGroup, AddFewChannels
from database import db, accs_action
from data.config_telethon_scheme import TelethonConnect
from data.config_aiogram import aiogram_bot
from filters.known_user import KnownUser
router = Router()
router.message.filter(
    KnownUser()
)


async def group_in_table(group_id):
    group_ids = await db.db_get_all_telegram_grp_id()
    if group_id in group_ids:
        return True
    return False


async def get_channel_id(link: str) -> int:
    chat = await aiogram_bot.get_chat(link)
    return chat.id

async def normalize_channel_link(link: str) -> str:
    if link.startswith('https://t.me/joinchat'):
        return link.split('/')[-1]
    if link.startswith('https://t.me/'):
        return '@' + link.split('https://t.me/')[1]
    return link

async def normalize_group_link(link: str) -> str:
    if link.startswith('https://t.me/+'):
        return link
    if link.startswith('https://t.me/'):
        return link
    if link.lower() == 'нет':
        return link.lower()
    else:
        return None

async def all_accs_join_channel(message, group_link):
    accounts = await accs_action.db_get_all_tg_accounts()
    monitor = await accs_action.db_get_monitor_account()
    if accounts:
        for acc in accounts:
            session = TelethonConnect(acc)
            res = await session.join_group(group_link)
            if res == 'already_in_group':
                await message.answer(f'{acc} уже состоит в канале {group_link}')
            elif res == 'banned':
                await message.answer(f'{acc} заблокирован')
            elif res == 'joined':
                await message.answer(f'{acc} успешно вступил в канал {group_link}')
            else:
                await message.answer(f'{acc} ошибка при вступлении в канал {group_link}')

        # вступление монитора в канал?
        # for mon in monitor:
        #     session = TelethonConnect(mon)
        #     res = await session.join_group(group_link)
        #     if res == 'already_in_group':
        #         await message.answer(f'{mon} уже состоит в канале {group_link}')
        #     elif res == 'banned':
        #         await message.answer(f'{mon} заблокирован')
        #     elif res == 'joined':
        #         await message.answer(f'{mon} успешно вступил в канал {group_link}')
        #     else:
        #         await message.answer(f'{mon} ошибка при вступлении в канал {group_link}')

    else:
        await message.answer('Нет добавленных аккаунтов')
        return


@router.callback_query(F.data == 'groups_add', KnownUser())
async def input_channel(callback: CallbackQuery, state: FSMContext):
    #await callback.message.delete()
    await callback.message.answer('Пожалуйста, введите ссылку на канал в поддерживаемом формате:\n\n'
                                  'Пример:\n@channel_name\nhttps://t.me/channel_name',
                                  reply_markup=kb_admin.groups_back())
    await state.set_state(AddGroup.input_channel)
    print(await state.get_state())


@router.message(AddGroup.input_channel)
async def add_channel(message: Message, state: FSMContext):
    try:
        uid = message.from_user.id
        group_name = await normalize_channel_link(message.text)
        if group_name.startswith('https://t.me/joinchat'):
            group_id = 999999999
        else:
            group_id = await get_channel_id(group_name)
        print(group_id)
        await state.update_data(group_name=group_name, group_id=group_id)
        await message.answer('Введите ссылку на группу для обсуждений, привязанную к каналу: '
                             '\n\nЕсли группа для обсуждений <b>не приватная и не требует вступления</b>, введите <b>нет</b>'
                             '\nЕсли группа приватная, то комментинг в такую группу <b>не доступен</b>.'
                             '\n\nПример: https://t.me/group_name', parse_mode='HTML')

        await state.set_state(AddGroup.input_discussion)

    except Exception as e:
        logger.error(e)
        await message.answer('Канал не найден'
                             '\n\nОтменить /cancel')






@router.message(AddGroup.input_discussion)
async def add_to_database(message: Message, state: FSMContext):
    discussion_link = await normalize_group_link(message.text)
    if not discussion_link:
        await message.answer('Ссылка на группу введена не верно.\n'
                             'Пожалуйста, попробуйте еще раз'
                             '\n\nОтменить /cancel')
        return

    uid = message.from_user.id
    state_data = await state.get_data()
    channel_name = state_data['group_name']
    channel_id = state_data['group_id']

    if not await group_in_table(channel_id):
        await db.db_add_telegram_group(uid, channel_name, channel_id, discussion_link)
        await message.answer(f'Канал {channel_name} добавлен.'
                             f'\nГруппа для комментариев: {discussion_link}')

        await message.answer('Настройки телеграм каналов:', reply_markup=kb_admin.group_settings_btns())
        logger.info(f'Channel {channel_name} added to database')
        await state.clear()

    else:
        await message.answer(f'Канал {channel_name} уже существует в базе данных.')
        await message.answer('Настройки телеграм каналов:', reply_markup=kb_admin.group_settings_btns())
        logger.info(f'Group {channel_name} already exists in database')
        await state.clear()



@router.message(Command(commands='add_few_channels'))
async def add_few_channels(message: Message, state: FSMContext):
    await message.answer('Введите список каналов:')
    await state.set_state(AddFewChannels.input_list)

@router.message(AddFewChannels.input_list)
async def process_add_few_channels(message: Message, state: FSMContext):
    uid = message.from_user.id
    channel_list = message.text.split('\n')
    print(channel_list)
    for channel in channel_list:
        try:
            channel = await normalize_channel_link(channel)
            channel_id = await get_channel_id(channel)
            if not await group_in_table(channel_id):
                await db.db_add_telegram_group(uid, channel, channel_id, 'нет')
                await message.answer(f'Канал {channel} добавлен')
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(e)
            continue
    await state.clear()