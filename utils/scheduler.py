import asyncio
import random
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_action import db_get_all_tg_accounts, db_get_all_telegram_groups, get_groups_and_triggers, db_get_monitor_account

scheduler = AsyncIOScheduler()

monitoring_enabled = False


class ChatMonitor:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.monitoring_enabled = False
        self.telethon_connect = None

    async def start_monitoring(self):
        if self.monitoring_enabled:
            return

        accounts = await db_get_monitor_account()
        if not accounts:
            raise Exception('В таблице нет аккаунтов для мониторинга.')

        if self.telethon_connect is None:
            monitor_account = random.choice(accounts)
            self.telethon_connect = TelethonConnect(monitor_account)

        groups_triggers = await get_groups_and_triggers()

        self.scheduler.add_job(self.telethon_connect.monitor_channels, 'interval', minutes=1, args=(groups_triggers,),
                               max_instances=10)
        self.scheduler.start()
        self.monitoring_enabled = True
        logger.info('Monitoring started')

        while True:
            await asyncio.sleep(1)

    async def stop_monitoring(self):
        if not self.monitoring_enabled:
            return

        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        self.monitoring_enabled = False
        logger.info('Monitoring disabled')

    async def get_status(self):
        return self.monitoring_enabled