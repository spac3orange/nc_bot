from telethon import TelegramClient
from telethon.sessions import StringSession
from environs import Env
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerUser


class AuthTelethon:
    def __init__(self, phone):
        self.phone = phone
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')
        self.session_file = '{}.session'.format(self.phone)
        print(self.api_id, self.api_hash, self.phone, type(self.phone))

    async def login(self):
        print('Попытка подключения')
        client = TelegramClient(self.session_file, self.api_id, self.api_hash)
        if not await self.session_exists():
            try:
                print('Файл сессии не найден. Создаю новый файл.')
                await client.connect()  # Установить соединение
                await client.send_code_request(self.phone)
                code = input('Введите код подтверждения: ')
                await client.sign_in(phone=self.phone, code=code)
            except Exception as e:
                print('Ошибка авторизации:', e)
                return False
        else:
            await client.connect()
        print('Подключение успешно')

        if await client.is_user_authorized():
            print('Успешный вход')
            await self.send_message(client, 'hello', 'plohoijoi')
            return True

        return True

    async def session_exists(self):
        import os
        return os.path.exists(self.session_file)

    async def send_message(self, client, message, username):
        try:
            entity = await client.get_input_entity(username)
            await client(SendMessageRequest(
                peer=entity,
                message=message
            ))
            print('Сообщение отправлено')
        except Exception as e:
            print('Ошибка отправки сообщения:', e)

# class TelethonConnect:
#     def __init__(self, session_name):
#         self.session_name = session_name
#         self.client =

