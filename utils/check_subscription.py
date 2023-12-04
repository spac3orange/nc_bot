from database import subscription
from data import logger

async def check_users_subscription():
    logger.info('Schedule check_users_subscription is working...')
    res = await subscription.check_subscription_expiry()
    if res:
        logger.warning(f'Users {res} have expired subscription. Their subscription data were cleared from database.')
    else:
        logger.info('No users with expired subscription.')