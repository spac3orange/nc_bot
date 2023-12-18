import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from data import aiogram_bot
from data.logger import logger
from keyboards import set_commands_menu
from handlers import (start, settings, monitoring, help, get_history,
                      pro_settings_menu, lk, monitoring_users, notifications,
                      pop_up_commands)
from handlers.users import users_handlers, promote_user, transfer_acc
from handlers.tg_accs import *
from handlers.gpt_accs import *
from handlers.groups import *
from handlers.admin import admin_panel, shop, stats
from handlers.payment import add_balance, ukassa
from database import db
from utils.scheduler import monitor, interval_operations
from middlewares import AntiSpamMiddleware


async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(tg_accs_settings.router)
    dp.include_router(user_tg_accs_settings.router)
    dp.include_router(promote_user.router)
    dp.include_router(transfer_acc.router)
    dp.include_router(notifications.router)
    dp.include_router(add_tg_acc.router)
    dp.include_router(del_tg_acc.router)
    dp.include_router(get_tg_accs.router)
    dp.include_router(tg_accs_monitor.router)
    dp.include_router(groups_settings.router)
    dp.include_router(pro_settings_menu.router)
    dp.include_router(add_group.router)
    dp.include_router(del_group.router)
    dp.include_router(get_groups.router)
    dp.include_router(promts.router)
    dp.include_router(triggers.router)
    dp.include_router(join_groups.router)
    dp.include_router(gpt_accs_settings.router)
    dp.include_router(add_gpt_acc.router)
    dp.include_router(del_gpt_acc.router)
    dp.include_router(get_gpt_accs.router)
    dp.include_router(default_prompt.router)
    dp.include_router(users_handlers.router)
    dp.include_router(lk.router)
    dp.include_router(add_balance.router)
    dp.include_router(ukassa.router)
    dp.include_router(admin_panel.router)
    dp.include_router(shop.router)
    dp.include_router(stats.router)
    dp.include_router(monitoring_users.router)
    dp.include_router(monitoring.router)
    dp.include_router(get_history.router)
    dp.include_router(pop_up_commands.router)
    dp.include_router(help.router)
    dp.include_router(settings.router)
    dp.include_router(start.router)

    dp.message.middleware(AntiSpamMiddleware())
    dp.callback_query.middleware(AntiSpamMiddleware())

    logger.info('Bot started')

    # Регистрируем меню команд
    await set_commands_menu(aiogram_bot)

    # инициализирем БД
    await db.db_start()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot)


async def main():
    task1 = asyncio.create_task(start_params())
    task2 = asyncio.create_task(monitor.stop_monitoring())
    task3 = asyncio.create_task(interval_operations.start_scheduled_tasks())
    await asyncio.gather(task1, task2, task3)


if __name__ == '__main__':
    try:
        while True:
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped')
    except Exception as e:
        logger.error(e)

