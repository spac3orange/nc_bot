import os
import random
from data import logger
import aiofiles
import json
from telethon import TelegramClient
import socks
import asyncio


async def format_proxy():
    username = 'customer-rtutu'
    password = 'd8BsmJb6G2T42DroWGocL'
    proxy_addr = 'uz-pr.oxylabs.io'
    proxy = (socks.SOCKS5, proxy_addr, 47000, True, username, password)
    return proxy


async def open_json(sess_name):
    for file in os.listdir('data/sessions_new'):
        if file == f'{sess_name}.json':
            async with aiofiles.open(f'data/sessions_new/{file}', 'r') as json_file:
                config = await json_file.read()
                config = json.loads(config)
                print(f'config {config}')
                if config:
                    return config
                else:
                    print(f'Ошибка создания сессии для {file}')
        else:
            continue


async def session_formatter(config_file):
    proxy = await format_proxy()
    if config_file:
        config = config_file
    else:
        print('Ошибка создания сессии')
        return
    print(config)
    name = config['session_file']
    client = TelegramClient(
        session=f'data/sessions_new/{config["session_file"]}',
        api_id=config['app_id'],
        api_hash=config['app_hash'],
        system_version=config['app_version'],
        device_model=config['device'],
        proxy=proxy
    )
    return client


async def check_session(sess_name):
    config = await open_json(sess_name)
    client = await session_formatter(config)
    if config and client:
        try:
            await client.connect()
            await asyncio.sleep(random.randint(1, 5))
            me = await client.get_me()
            if me:
                return True
            else:
                return False
        except Exception as e:
            logger.error(e)
        finally:
            await client.disconnect()
