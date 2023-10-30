from environs import Env
from aiogram import Bot


class TgBot:
    def __init__(self, token: str):
        self.token = token


class Config:
    def __init__(self, tg_bot: TgBot, admin_id: str):
        self.tg_bot = tg_bot
        self.admin_id = admin_id.split(',')


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')), admin_id=env('ADMIN_ID'))




config_aiogram = load_config()
aiogram_bot = Bot(token=config_aiogram.tg_bot.token)
