import asyncpg
from data import logger
from . db_action import db
import datetime

async def update_balance(user_id: int, amount: int):
    query = """
    UPDATE subscriptions
    SET balance = balance + $1
    WHERE user_id = $2
    """
    try:
        await db.execute_query(query, amount, user_id)
        logger.info(f"Updated balance for user_id {user_id}")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error updating balance for user_id {user_id}: {error}")


async def update_subscription_info(user_id: int, sub_type: int):
    current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sub_start_date = current_date
    if sub_type == 1:
        sub_end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m/%Y %H:%M:%S")
        balance_to_deduct = 300
    elif sub_type == 7:
        sub_end_date = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%d/%m/%Y %H:%M:%S")
        balance_to_deduct = 1500
    elif sub_type == 30:
        sub_end_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%d/%m/%Y %H:%M:%S")
        balance_to_deduct = 5000
    else:
        sub_end_date = "Нет"
        balance_to_deduct = 0

    query = """
    UPDATE subscriptions
    SET sub_start_date = $1, sub_end_date = $2, sub_type = $3, sub_status = TRUE
    WHERE user_id = $4
    """
    try:
        days = 'день' if sub_type == 1 else 'дней'
        await db.execute_query(query, sub_start_date, sub_end_date, f"Подписка на {sub_type} {days}", user_id)

        # Deduct balance
        balance_query = """
        UPDATE subscriptions
        SET balance = balance - $1
        WHERE user_id = $2
        """
        await db.execute_query(balance_query, balance_to_deduct, user_id)

        logger.info(f"Updated subscription info for user_id {user_id} and deducted balance: {balance_to_deduct}")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error updating subscription info for user_id {user_id}: {error}")