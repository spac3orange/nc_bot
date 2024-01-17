import asyncio
import datetime
import random
import re
from datetime import timedelta, datetime

import aiofiles
import pytz
from environs import Env
from telethon import TelegramClient, errors
from telethon.errors import UsernameOccupiedError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.functions.photos import DeletePhotosRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerChannel
from telethon.tl.types import InputPhoto

from data.config_aiogram import aiogram_bot
from data.logger import logger
from database import db, default_prompts_action, accs_action
from .chat_gpt import AuthOpenAI
from .proxy_config import proxy


async def extract_linked_chat_id(data):
    # Функция для рекурсивного обхода всех элементов словаря
    async def traverse_dict(dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                result = await traverse_dict(value)
                if result is not None:
                    return result
            elif isinstance(value, list):
                result = await traverse_list(value)
                if result is not None:
                    return result
            elif key == 'linked_chat_id':
                print(value)
                return value

    # Функция для рекурсивного обхода всех элементов списка
    async def traverse_list(lst):
        for item in lst:
            if isinstance(item, dict):
                result = await traverse_dict(item)
                if result is not None:
                    return result
            elif isinstance(item, list):
                result = await traverse_list(item)
                if result is not None:
                    return result

    return await traverse_dict(data)

async def monitor_settings(session):
    current_time = datetime.now().time()
    if current_time.hour == 0 and current_time.minute in [9, 10, 11]:
        logger.warning('Schedule skipped because it is cleanup time')
        return

    if await check_send_comments_running():
        logger.warning('Schedule skipped because send_comments is running')
        return
    active_users = await db.get_monitoring_user_ids()
    print('users with monitoring on:\n', active_users)
    if active_users:
        monitoring_list = []
        for u in active_users:
            user_settings = await db.get_user_groups_and_triggers(u)
            monitoring_list.append(user_settings)
        await session.monitor_channels(monitoring_list)
    else:
        logger.warning('No users to monitor')

async def check_send_comments_running():
    tasks = asyncio.all_tasks()
    for task in tasks:
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
        try:
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
        except Exception as e:
            logger.error(e)
            return False

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

        except (errors.UserDeactivatedBanError, errors.UserDeletedError) as e:
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
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, proxy=proxy)

    def get_env(self):
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')

    async def get_info(self, uid=None):
        table_name = 'telegram_accounts' if not uid else f'accounts_{uid}'
        phone = self.session_name.split('/')[-1].rstrip('.session')
        try:
            logger.info(f'Getting info about account {self.session_name}...')
            slp = random.randint(1, 3)
            await asyncio.sleep(slp)

            await self.client.connect()
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                full_me = await self.client(GetFullUserRequest(me.username))
                about = full_me.full_user.about or 'Не установлено'
                print(about)

                await self.client.disconnect()
                print(phone)
                await asyncio.sleep(slp)
                if uid:
                    sex = await accs_action.get_sex_by_phone(phone, uid)
                else:
                    sex = await accs_action.get_sex_by_phone(phone)
                print(f'Тел: {me.phone}\n'
                      f'ID: {me.id}\n'
                      f'Ник: {me.username}\n'
                      f'Пол: {sex}\n'
                      f'Биография: {about}\n'
                      f'Ограничения: {me.restricted}\n'
                      f'Причина ограничений: {me.restriction_reason}\n')

                return me.phone, me.id, me.first_name, me.last_name, me.username, me.restricted, about, sex
                # full = await self.client(GetFullUserRequest('username'))
            else:
                logger.error(f"Error connecting to account {self.session_name.split('/')[-1].rstrip('.session')}")
                return False
        except (errors.UserDeactivatedBanError, errors.UserDeletedError) as e:
            logger.error(f'account {self.session_name} is banned: {e}')
            update_status = asyncio.create_task(accs_action.change_acc_status(phone, table_name, 'Banned'))
            return False


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
            print(entity)
            await self.client(JoinChannelRequest(entity))
            logger.info('Joined group successfully')
            await self.client.disconnect()
            return 'joined'

        except (errors.UserDeactivatedBanError, errors.UserDeletedError) as e:
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
                            messages = await self.get_recent_messages(input_entity)
                            approved_messages.extend(self.filter_messages(messages, user_id, channel_name, keywords))
                await self.client.disconnect()
                print(approved_messages)
                if approved_messages:
                    await self.process_approved_messages(approved_messages)
            else:
                logger.warning('No channels to monitor')
        except Exception as e:
            logger.error(f'Error monitoring channels: {e}')
            print(e)
            await self.client.disconnect()

    async def get_recent_messages(self, input_entity):
        utc_now = datetime.now(pytz.utc)
        offset_date = utc_now - timedelta(minutes=2)
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
        return messages.messages

    def filter_messages(self, messages, user_id, channel_name, keywords):
        approved_messages = []
        for message in messages:
            if message.message and message.date > offset_date:
                if keywords == 'Нет':
                    if len(message.message) >= 300 and random.random() < 0.7:
                        logger.info('Found post without triggers')
                        approved_messages.append((user_id, channel_name, message))
                else:
                    for keyword in keywords.split(','):
                        if keyword.strip() in message.message:
                            logger.info('Found post with triggers')
                            approved_messages.append((user_id, channel_name, message))
        return approved_messages

    async def process_approved_messages(self, approved_messages):
        for msg in approved_messages:
            await self.process_approved_message(msg)

    async def process_approved_message(self, msg):
        user_id, channel, message = msg
        linked_chat = await db.db_get_group_link_by_channel_name(f'{channel}')
        if linked_chat is None:
            linked_chat = 'нет'
        if user_id in await db.get_user_ids_by_sub_type('DEMO'):
            await process_basic_user(user_id, channel, message, linked_chat)
        else:
            await process_regular_user(user_id, channel, message, linked_chat)

    async def process_basic_user(user_id, channel, message, linked_chat):
        if await db.get_comments_sent(user_id) < 1:
            acc = random.choice(await accs_action.get_phones_with_comments_today_less_than('telegram_accounts', 7))
            acc_sex = await accs_action.get_sex_by_phone(acc)
        else:
            try:
                await aiogram_bot.send_message(user_id, '<b>Демонстрационный период окончен.</b>'
                                                        '\n\nДля продолжения работы с ботом, пожалуйста оформите подписку в <b>Личном Кабинете</b>.',
                                               parse_mode='HTML')
                return
            except Exception as e:
                logger.error(e)
                return
        if not acc:
            logger.error('No accounts with comments less than 7')
            return
        await accs_action.set_in_work('telegram_accounts', acc)
        session = TelethonSendMessages(acc)
        await process_session(session, user_id, channel, message, acc, acc_sex, linked_chat)

    async def process_regular_user(user_id, channel, message, linked_chat):
        acc = random.choice(await accs_action.get_phones_with_comments_today_less_than(f'accounts_{user_id}', 7))
        acc_sex = await accs_action.get_sex_by_phone(acc, uid=user_id)
        if not acc:
            logger.error(f'No accounts with comments less than 7 for user {user_id}')
            return
        await accs_action.set_in_work(f'accounts_{user_id}', acc)
        session = TelethonSendMessages(acc)
        await process_session(session, user_id, channel, message, acc, acc_sex, linked_chat)

    async def process_session(session, user_id, channel, message, acc, acc_sex, linked_chat):
        acc_in_group = await session.join_group(channel)
        if acc_in_group == 'banned':
            print(f'{acc} banned')
            await aiogram_bot.send_message(user_id, f'Аккаунт {acc} заблокирован')
            return
        if linked_chat != 'нет':
            acc_in_disc = await session.join_group_disc(linked_chat)
            print(f'acc in disc {acc_in_disc}')
            if acc_in_disc == 'banned':
                print(f'{acc} banned')
                await aiogram_bot.send_message(user_id, f'Аккаунт {acc} заблокирован')
                return
        message_text = message.message
        promt = await get_prompt(channel, acc_sex)
        gpt_api = random.choice(await db.db_get_all_gpt_accounts())
        gpt = AuthOpenAI(gpt_api)
        gpt_question = message_text + '.' + f'{promt}'
        comment = await gpt.process_question(gpt_question)
        notif = user_id in await db.get_users_with_notifications()
        if comment:
            await db.update_comments_sent(user_id, 1)
            await session.send_comments(user_id, channel, message, acc, comment, notif, promt)
        else:
            print('Комментарий не сгенерирован')

    async def get_prompt(channel, acc_sex):
        all_promts = await db.db_get_all_promts()
        promt = all_promts.get(channel)
        promt_sex = 'Прокомментируй от лица мужчины.' if acc_sex == 'Мужской' else 'Прокомментируй от лица женщины.'
        if promt == 'Нет':
            default_prompts = await default_prompts_action.get_all_default_prompts()
            promt = random.choice(default_prompts) + f' {promt_sex}'
        else:
            promt = promt + f' {promt_sex}'
        return promt

class TelethonSendMessages:
    def __init__(self, session_name):
        self.get_env()
        self.session_name = 'data/telethon_sessions/{}.session'.format(session_name)
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, proxy=proxy)

    def get_env(self):
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')

    async def delete_comment(self, channel_name, msg):
        try:
            await self.client.connect()
            entity = await self.client.get_entity(channel_name)
            await self.client.delete_messages(entity, msg)
        except Exception as e:
            logger.error(e)

    async def send_comments(self, user_id, channel_name, message, acc, comment, notif, promt):
        print('incoming request:\n', user_id, channel_name, message, acc)
        try:
            await asyncio.sleep(random.randint(0, 40))
            if comment:
                comment = comment.strip('"')
                await self.client.connect()
                entity = await self.client.get_entity(channel_name)

                if message:
                    sent_msg = await self.client.send_message(entity=entity, message=comment, comment_to=message.id)
                    logger.info('Comment sent')
                    print(user_id, f'Комментарий в канал {channel_name} отправлен.')
                if notif:
                    await aiogram_bot.send_message(user_id, f'Комментарий в канал {channel_name} отправлен.')
                else:
                    logger.error('Message not found')
                await self.client.disconnect()
                write_history = asyncio.create_task(self.write_history(user_id, acc, channel_name, sent_msg, promt, comment))
            else:
                raise Exception('Comment not found')

        except Exception as e:
            logger.error(f'Error sending comments: {e}')
            print(e)
            await self.client.disconnect()
            write_error = asyncio.create_task(self.write_history(user_id, acc, channel_name, error=e))

    @staticmethod
    async def write_history(user_id, acc, channel_name, sent_msg=None, promt=None, comment=None, error=None):
        all_accs = await accs_action.db_get_all_tg_accounts()
        basic_acc = acc in all_accs
        table_name = 'telegram_accounts' if basic_acc else f'accounts_{user_id}'
        release_acc = asyncio.create_task(accs_action.set_in_work(table_name, acc, stop_work=True))
        if error:
            async with aiofiles.open(f'history/history_errors_{user_id}.txt', 'a', encoding='utf-8') as file:
                timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                await file.write(f'\n|{timestamp}'
                                 f'\nАккаунт: {acc}'
                                 f'\nКанал: {channel_name}'
                                 f'\nОшибка: \n{error}\n\n')
        else:
            if basic_acc:
                upd_comments = asyncio.create_task(accs_action.increment_comments('telegram_accounts', acc))
            else:
                upd_comments = asyncio.create_task(accs_action.increment_comments(f'accounts_{user_id}', acc))
            async with aiofiles.open(f'history/history_{user_id}.txt', 'a', encoding='utf-8') as file:
                timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                await file.write(f'\n|{timestamp}:'
                                 f'\n<b>Аккаунт</b>: {acc}'
                                 f'\n<b>Канал</b>: {channel_name}'
                                 f'\n<b>Id</b>: {sent_msg}'
                                 f'\n<b>Промт</b>: \n{promt}'
                                 f'\n<b>Комментарий</b>: \n{comment}\n\n')



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

        except (errors.UserDeactivatedBanError, errors.UserDeletedError) as e:
            logger.error(e)
            return 'banned'
        except Exception as e:
            logger.error(f'Error joining group: {e}')
            await self.client.disconnect()
            return False

    async def join_group_disc(self, linked_chat):
        try:
            slp = random.randint(8, 15)
            await asyncio.sleep(slp)
            logger.info(f'Joining channel_disc: {linked_chat}')
            await self.client.connect()

            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
            for dialog in groups_and_channels:
                dialog = await self.client.get_entity(dialog)
                dialog_username = dialog.username
                print(linked_chat.split('/')[-1])
                try:
                    if dialog_username == linked_chat.split('/')[-1]:
                        self.client.disconnect()
                        print('already_in_group')
                        return 'already_in_group'
                except Exception as e:
                    logger.error(e)
                    continue

            logger.info(f'Joining channel: {linked_chat}')
            entity = await self.client.get_entity(linked_chat)
            await self.client(JoinChannelRequest(linked_chat))
            logger.info('Joined group_disc successfully')

            await self.client.disconnect()
            return 'joined'

        except (errors.UserDeactivatedBanError, errors.UserDeletedError) as e:
            logger.error(e)
            return 'banned'
        except Exception as e:
            logger.error(f'Error joining group: {e}')
            await self.client.disconnect()
            return False

    async def delete_all_profile_photos(self):
        await self.client.connect()
        try:
            p = await self.client.get_profile_photos('me')
            print(p)
            for photo in p:
                await self.client(DeletePhotosRequest(
                    id=[InputPhoto(
                        id=photo.id,
                        access_hash=photo.access_hash,
                        file_reference=photo.file_reference
                    )]
                ))
                slp = random.randint(2, 4)
                await asyncio.sleep(slp)
            logger.info(f'avatars deleted for account {self.session_name.split("/")[-1]}"')
        except Exception as e:
            logger.error(f'Error deleting all avatars {e}')
        finally:
            await self.client.disconnect()

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