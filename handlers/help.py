from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from keyboards import kb_admin
from filters.is_admin import IsAdmin
router = Router()


@router.message(Command(commands='help_settings'))
async def help_settings(message: Message):
    await message.answer('Аккаунты TG - настройки телеграм аккаунтов.\n\n'
                         'Аккаунты GPT - настройки ChatGPT аккаунтов.\n\n'
                         'Каналы - настройки каналов, промтов и триггеров.\n\n'
                         'Вступить в каналы - вступить в каналы всеми внесенными в базу аккаунтами для последующей '
                         'отправки комментариев.')


@router.message(Command(commands='help_tg_accs'))
async def help_tg(message: Message):
    await message.answer('Добавить - добавить телеграм аккаунт в базу данных.\n\n'
                         'Удалить - удалить телеграм аккаунт из базы данных.\n\n'
                         'Монитор - выбрать телеграм аккаунт, который будет мониторить каналы на сообщения, '
                         'содержащие триггеры.\n\n'
                         'Информация - получить информацию о всех внесенных в базу данных аккаунтах.')

@router.message(Command(commands='help_accs'))
async def help_tg(message: Message):
    await message.answer('Здесь можно изменить инофрмацию аккаунта, такую как:\n'
                         '<b>Имя</b>, <b>Фамилия</b>, <b>Bio, Username</b>\n\n',
                         parse_mode='HTML')




@router.message(Command(commands='help_gpt_accs'))
async def help_gpt(message: Message):
    await message.answer('Добавить - добавить ChatGPT API ключ в базу данных.\n\n'
                         'Удалить - удалить ChatGPT API ключ из базы данных.\n\n'
                         'Токены - запросить информацию о токенах на балансе для каждого ChatGPT аккаунта.')


@router.message(Command(commands='help_channels'))
async def help_channels(message: Message):
    await message.answer('Добавить - добавить канал для мониторинга в базу данных.\n\n'
                         'Удалить - удалить канал из базы данных.\n\n'
                         'Список каналов - получить список внесенных в базу данных каналов.')

@router.message(Command(commands='help_promts'))
async def help_promts_triggers(message: Message):
    await message.answer('Триггеры - установить, удалить или изменить триггеры для канала.\n\n'
                         'Промты - установить, удалить или изменить промт, отправляемый ChatGPT для канала.\n\n')

@router.message(Command(commands='information'))
async def information(message: Message):
    await message.answer('Информация о боте:\n\n')
