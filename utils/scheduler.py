import asyncio
import random
from data.logger import logger
from data.config_telethon_scheme import TelethonConnect
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_action import db_get_all_tg_accounts, db_get_all_telegram_groups, get_groups_and_triggers, db_get_monitor_account

scheduler = AsyncIOScheduler()

monitoring_enabled = False


async def monitor_chats():
    monitor_account = random.choice(await db_get_monitor_account())
    groups_triggers = await get_groups_and_triggers()
    print(groups_triggers)

    sess = TelethonConnect(monitor_account)
    scheduler.start()
    scheduler.add_job(sess.monitor_channels, 'interval', minutes=1, seconds=30, args=(groups_triggers,))

    while True:
        await asyncio.sleep(1)


class ChatMonitor:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.monitoring_enabled = False

    async def start_monitoring(self):
        if self.monitoring_enabled:
            return

        accounts = await db_get_monitor_account()
        if not accounts:
            raise Exception('В таблице нет аккаунтов для мониторинга.')
        monitor_account = random.choice(accounts)
        groups_triggers = await get_groups_and_triggers()
        sess = TelethonConnect(monitor_account)

        self.scheduler.add_job(sess.monitor_channels, 'interval', minutes=1, args=(groups_triggers,))
        self.scheduler.start()
        self.monitoring_enabled = True
        logger.info('Monitoring started')

    async def stop_monitoring(self):
        if not self.monitoring_enabled:
            return

        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        self.monitoring_enabled = False
        logger.info('Monitoring disabled')

    async def get_status(self):
        return self.monitoring_enabled
