import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from states.states import CheckChannels
from aiogram.fsm.context import FSMContext
from utils import user_license
from database import accs_action
from data.config_telethon_scheme import TelethonConnect, TelethonSendMessages
from pprint import pprint

router = Router()


@router.message(Command(commands='user_license'))
async def send_user_license(message: Message):
    await message.answer(text=user_license.license_text, parse_mode='HTML')


@router.message(Command(commands='check_channels_list'))
async def p_check_chann_list(message: Message, state: FSMContext):
    await message.answer('Введите список каналов: ')
    await state.set_state(CheckChannels.input_list)


@router.message(CheckChannels.input_list)
async def p_chann_list(message: Message, state: FSMContext):
    uid = message.from_user.id
    channels_list = message.text.split()
    print(channels_list)
    user_accounts = await accs_action.get_user_accounts(uid)

    # Количество аккаунтов пользователя
    num_accounts = len(user_accounts)

    # Разделяем список каналов на несколько подсписков, каждый подсписок для одного аккаунта
    if num_accounts > 0:
        # Рассчитываем размер каждого подсписка
        size_of_each_list = len(channels_list) // num_accounts
        # Создаем список подсписков
        divided_lists = [channels_list[i:i + size_of_each_list] for i in range(0, len(channels_list), size_of_each_list)]
        # Если элементы остались не распределенными (из-за деления с остатком), добавляем их в последний подсписок
        if len(channels_list) % num_accounts != 0:
            divided_lists[-1].extend(channels_list[size_of_each_list * num_accounts:])
        # Для примера просто отправим каждый подсписок обратно пользователю
        tasks = []
        for sublist, acc in zip(divided_lists, user_accounts):
            pprint('sublist:', sublist)
            sess = TelethonSendMessages(acc)
            task = asyncio.create_task(sess.get_channel_linkage(sublist))
            tasks.append(task)
        res = await asyncio.gather(tasks)
        pprint(res)
    else:
        await message.answer('Недостаточно акаунтов.')