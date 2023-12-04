import datetime
from . import db
from data import logger


async def check_subscription_expiry():
    current_date = datetime.datetime.now()
    query = """ 
    UPDATE subscriptions 
    SET sub_start_date = CASE WHEN TO_TIMESTAMP(sub_end_date, 'DD/MM/YYYY HH24:MI:SS') < $1 THEN NULL ELSE sub_start_date END, 
        sub_end_date = CASE WHEN TO_TIMESTAMP(sub_end_date, 'DD/MM/YYYY HH24:MI:SS') < $1 THEN NULL ELSE sub_end_date END, 
        sub_status = CASE WHEN TO_TIMESTAMP(sub_end_date, 'DD/MM/YYYY HH24:MI:SS') < $1 THEN FALSE ELSE sub_status END 
    WHERE TO_TIMESTAMP(sub_end_date, 'DD/MM/YYYY HH24:MI:SS') < $1 
    RETURNING user_id
    """
    try:
        result = await db.pool.fetch(query, current_date)
        user_ids = [row['user_id'] for row in result]
        logger.info("Updated subscription status for expired subscriptions")
        return user_ids
    except Exception as e:
        logger.error(f"Error updating subscription status: {e}")
