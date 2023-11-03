import asyncio
import random
from telethon import TelegramClient, errors
from environs import Env
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel, Channel, PeerChannel
from data.logger import logger
from database.db_action import db_get_all_tg_accounts, db_get_promts_for_group, db_get_all_gpt_accounts, db_get_users
from telethon.tl.functions.channels import JoinChannelRequest
from pprint import pprint
import datetime
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import timedelta, datetime
import pytz
from .chat_gpt import AuthOpenAI
import re
from data.config_aiogram import aiogram_bot


async def remove_links(text):
    # Фильтрация ссылок
    filtered_text = re.sub(r'http\S+|www.\S+', '', text)

    return filtered_text


class AuthTelethon:
    def __init__(self, phone):
        self.phone = phone
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')
        self.session_file = 'data/telethon_sessions/{}.session'.format(self.phone)
        print(self.api_id, self.api_hash, self.phone, type(self.phone))
        self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)


    async def login_phone(self):
        try:
            logger.info('Attempting to connect')
            await self.client.connect()  # Установить соединение
            await self.client.send_code_request(self.phone)
            logger.info(f'Auth code sent to telegram account {self.phone}')
            return True

        except Exception as e:
            logger.error('Authorization error')
            return False


    async def login_process_code(self, code=None, password=None):
        logger.info('Attempting to sign in...')
        if code:
            if password:
                print(1)
                print(password)
                await self.client.sign_in(phone=self.phone, code=code, password=password)
            else:
                print(2)
                await self.client.sign_in(phone=self.phone, code=code)

        else:
            await self.client.sign_in(password=password)

        if await self.client.is_user_authorized():
            logger.info(f'Signed in in {self.phone}')
            await self.client.disconnect()
            return True

        return True

    async def send_message(self, client, message, username):
        try:
            entity = await client.get_input_entity(username)
            await client(SendMessageRequest(
                peer=entity,
                message=message
            ))
            logger.info('Message sent')
        except Exception as e:
            logger.error(f'Error {e}')


    async def join_group(self, group_link):
        try:
            logger.info(f'Joining channel: {group_link}')
            await self.client.connect()
            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
            for dialog in groups_and_channels:
                dialog = await self.client.get_entity(dialog)
                dialog_id = dialog.id
                print(dialog_id)
                try:
                    if dialog_id == group_link:
                        self.client.disconnect()
                        return 'already_in_group'
                except Exception as e:
                    logger.error(e)
                    continue

            entity = await self.client.get_entity(group_link)

            await self.client(JoinChannelRequest(entity))
            logger.info('Joined group successfully')
            await self.client.disconnect()
            return 'joined'

        except errors.UserDeactivatedBanError as e:
            logger.error(e)
            return 'banned'
        except Exception as e:
            logger.error(f'Error joining group: {e}')
            await self.client.disconnect()
            return False


class TelethonConnect:
    def __init__(self, session_name):
        self.get_env()
        self.session_name = 'data/telethon_sessions/{}.session'.format(session_name)
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    def get_env(self):
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')

    async def get_info(self):
        logger.info(f'Getting info about account {self.session_name}...')
        await self.client.connect()
        me = await self.client.get_me()
        print(f'Тел: {me.phone}\n'
              f'ID: {me.id}\n'
              f'Ник: {me.username}\n'
              f'Ограничения: {me.restricted}\n'
              f'Причина ограничений: {me.restriction_reason}\n')
        await self.client.disconnect()
        return me.phone, me.id, me.first_name, me.last_name, me.username, me.restricted
        # full = await self.client(GetFullUserRequest('username'))

    async def join_group(self, group_link):
        try:
            logger.info(f'Joining channel: {group_link}')
            await self.client.connect()
            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
            for dialog in groups_and_channels:
                dialog = await self.client.get_entity(dialog)
                dialog_id = dialog.id
                print(dialog_id)
                try:
                    if dialog_id == group_link:
                        self.client.disconnect()
                        return 'already_in_group'
                except Exception as e:
                    logger.error(e)
                    continue

            entity = await self.client.get_entity(group_link)

            await self.client(JoinChannelRequest(entity))
            logger.info('Joined group successfully')
            await self.client.disconnect()
            return 'joined'

        except errors.UserDeactivatedBanError as e:
            logger.error(e)
            return 'banned'
        except Exception as e:
            logger.error(f'Error joining group: {e}')
            await self.client.disconnect()
            return False

    async def monitor_channels(self, channel_keywords: dict):
        try:
            logger.info('Monitoring channels for new posts...')
            await self.client.connect()
            approved_messages = []
            for channel, keywords in channel_keywords.items():
                entity = await self.client.get_entity(channel)
                input_entity = InputPeerChannel(entity.id, entity.access_hash)
                utc_now = datetime.now(pytz.utc)
                offset_date = utc_now - timedelta(minutes=1)

                messages = await self.client(GetHistoryRequest(
                    peer=input_entity,
                    limit=10,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                for message in messages.messages:
                    if message.message and message.date > offset_date:
                        for keyword in keywords.split(','):
                            if keyword.strip() in message.message:
                                #pprint({
                                #   'channel': channel,
                                #   'message_id': message.id,
                                #    'text': message.message
                                #})
                                logger.info('Found post with triggers')

                                approved_messages.append((channel, message))
                                break
            await self.client.disconnect()
            if approved_messages:
                accounts = await db_get_all_tg_accounts()
                tasks = []
                for msg in approved_messages:
                    acc = random.choice(accounts)
                    channel, message = msg
                    session = TelethonSendMessages(acc)
                    task = asyncio.create_task(session.send_comments(channel, message, acc))
                    tasks.append(task)
                await asyncio.gather(*tasks)



        except Exception as e:
            logger.error(f'Error monitoring channels: {e}')
            await self.client.disconnect()


class TelethonSendMessages:
    def __init__(self, session_name):
        self.get_env()
        self.session_name = 'data/telethon_sessions/{}.session'.format(session_name)
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    def get_env(self):
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')

    async def send_comments(self, channel_name, message, acc):
        try:
            message_text = await remove_links(message.message.lower())

            promt = await db_get_promts_for_group(channel_name)
            gpt_api = random.choice(await db_get_all_gpt_accounts())
            gpt_question = message_text + '.' + f'{promt}'
            print(gpt_api)
            pprint(gpt_question)

            gpt = AuthOpenAI(gpt_api)
            comment = await gpt.process_question(gpt_question)

            if comment:
                comment = comment.strip('"')
                await self.client.connect()
                entity = await self.client.get_entity(channel_name)

                if message:
                    await self.client.send_message(entity=entity, message=comment, comment_to=message.id)
                    logger.info('Comment sent')
                    users = await db_get_users()
                    for u in users:
                        await aiogram_bot.send_message(u[0], f'Комментарий в группу {channel_name} отправлен.')
                else:
                    logger.error('Message not found')
                await self.client.disconnect()

                # Запись отправленного комментария в файл
                with open('history.txt', 'a', encoding='utf-8') as file:
                    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                    file.write(f'\n|{timestamp}:'
                               f'\nАккаунт: {acc}'
                               f'\nКомментарий: \n{comment}\n\n')
            else:
                raise Exception('Comment not found')

        except Exception as e:
            logger.error(f'Error sending comments: {e}')
            await self.client.disconnect()

            # Запись ошибки в файл
            with open('history.txt', 'a', encoding='utf-8') as file:
                timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                file.write(f'\n|{timestamp}'
                           f'\nАккаунт: {acc}'
                           f'\nОшибка: \n{e}\n\n')
