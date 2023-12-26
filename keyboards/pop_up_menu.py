from aiogram.types import BotCommand


async def set_commands_menu(bot):
    """
        Set up the main menu commands for the bot.
        Args:
            bot (telegram.Bot): The Telegram bot instance.
        Returns:
            None
        """
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Главное меню'),
        BotCommand(command='/monitoring_status',
                   description='Статус мониторинга'),
        BotCommand(command='/support',
                   description='Тех. Поддержка'),
        BotCommand(command='/information',
                   description='Информация о боте'),
        BotCommand(command='/user_license',
                   description='Пользовательское соглашение'),
    ]

    await bot.set_my_commands(main_menu_commands)
