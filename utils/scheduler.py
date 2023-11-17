import asyncio
import random
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect, monitor_settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import db

scheduler = AsyncIOScheduler()

monitoring_enabled = False


class ChatMonitor:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.monitoring_enabled = False
        self.telethon_connect = None
        self.clients = []

    async def start_monitoring(self):
        try:
            if self.monitoring_enabled:
                return

            accounts = await db.db_get_monitor_account()
            if not accounts:
                raise Exception('В таблице нет аккаунтов для мониторинга.')

            if self.telethon_connect is None:
                monitor_account = random.choice(accounts)
                self.telethon_connect = TelethonConnect(monitor_account)

            self.scheduler.add_job(monitor_settings, 'interval', minutes=1, args=(self.telethon_connect,),
                                   max_instances=10)

            self.scheduler.start()
            self.monitoring_enabled = True
            logger.info('Monitoring started')

            while True:
                await asyncio.sleep(1)

        except Exception as e:
            raise Exception(e)

    async def add_user(self, user_id):
        if user_id not in self.clients:
            user_settings = await db.get_user_groups_and_triggers(user_id)
            self.clients.append(user_settings)
            logger.info(f'Добавлен пользователь {user_id} в мониторинг')
            print('Клиенты:', self.clients)

    async def del_user(self, user_id):
        for c in self.clients:
            if c['user_id'] == user_id:
                self.clients.remove(c)
                logger.info(f'Удален пользователь {user_id} из мониторинга')
                print('Клиенты:', self.clients)

    async def stop_monitoring(self):
        if not self.monitoring_enabled:
            return

        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        self.monitoring_enabled = False
        logger.info('Monitoring disabled')

    async def get_status(self):
        return self.monitoring_enabled


class UsersToday:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_scheduler(self):
        self.scheduler.add_job(db.clear_users_today, 'cron', hour=0, minute=0)
        self.scheduler.start()
        logger.info('users_today scheduler started')


format_users_today = UsersToday()
monitor = ChatMonitor()
