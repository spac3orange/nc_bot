import asyncio
import random
from telethon import TelegramClient, errors
from environs import Env
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel
from data.logger import logger
from database import db
from telethon.tl.functions.channels import JoinChannelRequest
import datetime
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import timedelta, datetime
import pytz
from .chat_gpt import AuthOpenAI
import re
from data.config_aiogram import aiogram_bot
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.types import InputPhoto
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameOccupiedError
import mimetypes


async def monitor_settings(session):
    current_time = datetime.now().time()
    if current_time.hour == 0 and current_time.minute in [9, 10, 11]:
        logger.warning('Schedule skipped because it is cleanup time')
        return

    if await check_send_comments_running():
        logger.warning('Schedule skipped because send_comments is running')
        return
    active_users = await db.get_monitoring_user_ids()
    print('active_users\n', active_users)
    if active_users:
        monitoring_list = []
        for u in active_users:
            user_settings = await db.get_user_groups_and_triggers(u)
            print('user_settings', user_settings)
            monitoring_list.append(user_settings)
        print('outp request\n', monitoring_list)
        await session.monitor_channels(monitoring_list)
    else:
        logger.warning('No users to monitor')

async def check_send_comments_running():
    tasks = asyncio.all_tasks()
    for task in tasks:
        print(task.get_coro().__qualname__)
        if task.get_coro().__qualname__ == 'TelethonSendMessages.send_comments':
            return True
    return False


async def remove_links(text):
    # Фильтрация ссылок
    filtered_text = re.sub(r'http\S+|www.\S+', '', text)

    return filtered_text


class AuthTelethon:
    def __init__(self, phone: str):
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
                dialog_username = dialog.username
                print(f'dialog_username: {dialog_username}')
                print(f'dialog_link: {group_link}')
                try:
                    if dialog_username == group_link:
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

    async def change_first_name(self, first_name: str):
        try:
            await self.client.connect()
            await self.client(UpdateProfileRequest(first_name=first_name))
            logger.info(f'Changed first name to {first_name}')
            await self.client.disconnect()
            return True
        except Exception as e:
            logger.error(f'Error changing first name: {e}')
            await self.client.disconnect()
            return False

    async def change_last_name(self, last_name: str):
        try:
            await self.client.connect()
            await self.client(UpdateProfileRequest(last_name=last_name))
            logger.info(f'Changed last name to {last_name}')
            await self.client.disconnect()
            return True
        except Exception as e:
            logger.error(f'Error changing last name: {e}')
            await self.client.disconnect()
            return False

    async def change_username(self, username: str):
        try:
            await self.client.connect()
            await self.client(UpdateUsernameRequest(username))
            logger.info(f'Changed username to {username}')
            await self.client.disconnect()
            return 'done'
        except UsernameOccupiedError as e:
            logger.error(f'Error changing username: {e}')
            await self.client.disconnect()
            return 'username_taken'
        except Exception as e:
            logger.error(f'Error changing username: {e}')
            await self.client.disconnect()
            return False

    async def change_bio(self, bio: str):
        try:
            await self.client.connect()
            await self.client(UpdateProfileRequest(about=bio))
            logger.info('Changed bio')
            await self.client.disconnect()
            return True
        except Exception as e:
            logger.error(f'Error changing bio: {e}')
            await self.client.disconnect()
            return False

    async def change_profile_photo(self, photo_path: str):
        try:
            await self.client.connect()
            await self.client(UploadProfilePhotoRequest(
                file=await self.client.upload_file(photo_path)
            ))
            logger.info('Changed profile photo')
            return True
        except Exception as e:
            logger.error(f'Error changing profile photo: {e}')
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

        full_me = await self.client(GetFullUserRequest(me.username))
        about = full_me.full_user.about or 'Не установлено'
        print(about)
        print(f'Тел: {me.phone}\n'
              f'ID: {me.id}\n'
              f'Ник: {me.username}\n'
              f'Биография: {about}\n'
              f'Ограничения: {me.restricted}\n'
              f'Причина ограничений: {me.restriction_reason}\n')
        await self.client.disconnect()
        return me.phone, me.id, me.first_name, me.last_name, me.username, me.restricted, about
        # full = await self.client(GetFullUserRequest('username'))

    async def join_group(self, group_link):
        try:
            logger.info(f'Joining channel: {group_link}')
            await self.client.connect()
            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
            for dialog in groups_and_channels:
                dialog = await self.client.get_entity(dialog)
                dialog_username = dialog.username
                print(dialog_username)
                print(group_link[1:])
                try:
                    if dialog_username == group_link[1:]:
                        self.client.disconnect()
                        print('already_in_group')
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

    async def monitor_channels(self, channel_keywords: dict = None):
        try:
            if channel_keywords:
                logger.info('Monitoring channels for new posts...')
                await self.client.connect()
                approved_messages = []
                for item in channel_keywords:
                    for user_id, channels in item.items():
                        for (channel_name, channel_id), keywords in channels.items():
                            try:
                                entity = await self.client.get_entity(channel_name)
                            except Exception as e:
                                continue
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

                            if keywords == 'Нет':
                                for message in messages.messages:
                                    if message.message and message.date > offset_date:
                                        if len(message.message) > 300:
                                            logger.info('Found post without triggers')
                                            approved_messages.append((user_id, channel_name, message))

                            else:
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

                                                approved_messages.append((user_id, channel_name, message))

                await self.client.disconnect()
                if approved_messages:
                    gpt_accs = await db.db_get_all_gpt_accounts()
                    all_promts = await db.db_get_all_promts()
                    all_users_with_notif = await db.get_users_with_notifications()
                    all_basic_users = await db.get_user_ids_by_sub_type('DEMO')
                    # for m in approved_messages:
                    #     user_id = m[0]
                    #     try:
                        
                    tasks = []
                    for msg in approved_messages:
                        basic = False
                        user_id, channel, message = msg
                        if user_id in all_basic_users:
                            if await db.get_comments_sent(user_id) < 1:
                                acc = random.choice(await db.get_phones_with_comments_today_less_than('telegram_accounts', 7))
                            else:
                                try:
                                    await aiogram_bot.send_message(user_id, '<b>Демонстрационный период окончен.</b>'
                                                                            '\n\nДля продолжения работы с ботом, пожалуйста оформите подписку в <b>Личном Кабинете</b>.',
                                                                   parse_mode='HTML')
                                    continue
                                except Exception as e:
                                    logger.error(e)
                                    continue
                            if acc:
                                session = TelethonSendMessages(acc)
                                basic = True
                            else:
                                logger.error('No accounts with comments less than 7')
                                continue
                        else:
                            acc = random.choice(await db.get_phones_with_comments_today_less_than(f'accounts_{user_id}', 7))
                            if acc:
                                session = TelethonSendMessages(acc)
                            else:
                                logger.error(f'No accounts with comments less than 7 for user {user_id}')
                                continue
                        acc_in_group = await session.join_group(channel)

                        if acc_in_group == 'already_in_group':
                            pass
                            print(f'{acc} already in group {channel}')
                        elif acc_in_group == 'joined':
                            print(f'{acc} joined group {channel}')
                        elif acc_in_group == 'banned':
                            print(f'{acc} banned')
                            await aiogram_bot.send_message(user_id, f'Аккаунт {acc} заблокирован')
                            continue

                        message_text = message.message
                        promt = all_promts.get(channel)
                        if promt == 'Нет':
                            promt = 'Напиши короткий комментарий от первого лица размером в одно предложение. Веди ' \
                                    'себя как реальный человек, не используй шаблонных фраз и будь на позитиве.'
                        gpt_api = random.choice(gpt_accs)
                        gpt = AuthOpenAI(gpt_api)
                        gpt_question = message_text + '.' + f'{promt}'
                        comment = await gpt.process_question(gpt_question)
                        notif = None
                        if user_id in all_users_with_notif:
                            notif = True
                        if comment:
                            if basic:
                                await db.increment_comments('telegram_accounts', acc)
                            else:
                                await db.increment_comments(f'accounts_{user_id}', acc)

                            await db.update_comments_sent(user_id, 1)
                            asyncio.create_task(session.send_comments(user_id, channel, message,
                                                                      acc, comment, notif))

                        else:
                            print('Комментарий не сгенерирован')

            else:
                logger.warning('No channels to monitor')


        except Exception as e:
            logger.error(f'Error monitoring channels: {e}')
            print(e)
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

    async def send_comments(self, user_id, channel_name, message, acc, comment, notif):
        print('incoming request:\n', user_id, channel_name, message, acc)
        try:
            await asyncio.sleep(random.randint(0, 40))
            if comment:
                comment = comment.strip('"')
                await self.client.connect()
                entity = await self.client.get_entity(channel_name)

                if message:
                    await self.client.send_message(entity=entity, message=comment, comment_to=message.id)
                    logger.info('Comment sent')
                    print(user_id, f'Комментарий в канал {channel_name} отправлен.')
                if notif:
                    await aiogram_bot.send_message(user_id, f'Комментарий в канал {channel_name} отправлен.')
                else:
                    logger.error('Message not found')
                await self.client.disconnect()

                # Запись отправленного комментария в файл
                with open(f'history/history_{user_id}.txt', 'a', encoding='utf-8') as file:
                    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                    file.write(f'\n|{timestamp}:'
                               f'\nАккаунт: {acc}'
                               f'\nКанал: {channel_name}'
                               f'\nКомментарий: \n{comment}\n\n')
            else:
                raise Exception('Comment not found')

        except Exception as e:
            logger.error(f'Error sending comments: {e}')
            print(e)
            await self.client.disconnect()

            # Запись ошибки в файл
            with open(f'history/history_{user_id}.txt', 'a', encoding='utf-8') as file:
                timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                file.write(f'\n|{timestamp}'
                           f'\nАккаунт: {acc}'
                           f'\nКанал: {channel_name}'
                           f'\nОшибка: \n{e}\n\n')

    async def join_group(self, group_link):
        try:
            logger.info(f'Joining channel: {group_link}')
            await self.client.connect()
            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
            for dialog in groups_and_channels:
                dialog = await self.client.get_entity(dialog)
                dialog_username = dialog.username
                print(dialog_username)
                print(group_link[1:])
                try:
                    if dialog_username == group_link[1:]:
                        self.client.disconnect()
                        print('already_in_group')
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

