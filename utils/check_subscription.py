from database import subscription, db, accs_action
from data import logger, aiogram_bot

async def check_users_subscription():
    logger.info('Schedule check_users_subscription is working...')
    res = await subscription.check_subscription_expiry()
    for i in res:
        await accs_action.return_accounts(i)
        await aiogram_bot.send_message(chat_id=i, text='Ваша подписка истекла.'
                                                       '\nTelegram аккаунты будут изъяты через 48 часов.', parse_mode='HTML')
        logger.info(f'Accounts from {i}_accounts were returned to accounts_telegram table.')
    if res:
        logger.warning(f'Users {res} have expired subscription. Their subscription data were cleared from database.')
    else:
        logger.info('No users with expired subscription.')