from database import subscription, db
from data import logger

async def check_users_subscription():
    logger.info('Schedule check_users_subscription is working...')
    res = await subscription.check_subscription_expiry()
    for i in res:
        await db.return_accounts(i)
        logger.info(f'Accounts from {i}_accounts were returned to accounts_telegram table.')
    if res:
        logger.warning(f'Users {res} have expired subscription. Their subscription data were cleared from database.')
    else:
        logger.info('No users with expired subscription.')