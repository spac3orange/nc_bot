import asyncpg
from data import logger
from . db_action import db
from typing import List


async def db_get_shop_accs() -> List[str]:
    """
    Retrieves all Telegram accounts from the database.
    """
    try:
        query = "SELECT phone FROM accs_shop"
        rows = await db.fetch_all(query)
        phone_numbers = [row[0] for row in rows]
        return phone_numbers
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving Telegram accounts from the accs_shop: {error}")
        return []


async def transfer_accounts_to_shop(amount: int):
    try:
        async with db.pool.acquire() as conn:
            # Получаем указанное количество аккаунтов из таблицы telegram_accounts
            accounts = await conn.fetch(f"""
                SELECT phone FROM telegram_accounts LIMIT {amount}
            """)

            # Перемещаем аккаунты в таблицу accs_shop
            for account in accounts:
                phone = account['phone']
                await conn.execute(f"""
                    INSERT INTO accs_shop (phone) VALUES ($1)
                """, phone)

            # Удаляем перемещенные аккаунты из таблицы telegram_accounts
            await conn.execute(f"""
                DELETE FROM telegram_accounts WHERE phone IN (
                    SELECT phone FROM telegram_accounts LIMIT {amount}
                )
            """)
        return True
    except (Exception, asyncpg.PostgresError) as error:
        print("Error while transferring accounts", error)
        return False


async def transfer_sold_accounts(user_id: int, amount: int):
    cost = 200
    try:
        async with db.pool.acquire() as conn:
            # Списываем деньги с баланса
            await conn.execute(f"""
                            UPDATE subscriptions SET balance = balance - {amount * cost} WHERE user_id = {user_id}
                        """)

            # Создаем таблицу extra_accounts_{user_id}, если она не существует
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS extra_accounts_{user_id} (
                    phone TEXT PRIMARY KEY,
                    comments INTEGER DEFAULT 0,
                    comments_today INTEGER DEFAULT 0,
                    sex TEXT DEFAULT 'Мужской',
                    status TEXT DEFAULT 'Active',
                    in_work BOOLEAN DEFAULT FALSE
                )
            """)

            # Получаем указанное количество аккаунтов из таблицы accs_shop
            accounts = await conn.fetch(f"""
                SELECT phone FROM accs_shop LIMIT {amount}
            """)

            # Перемещаем аккаунты в таблицу extra_accounts_{user_id}
            for account in accounts:
                phone = account['phone']
                await conn.execute(f"""
                    INSERT INTO extra_accounts_{user_id} (phone) VALUES ($1)
                """, phone)

            # Удаляем перемещенные аккаунты из таблицы accs_shop
            await conn.execute(f"""
                DELETE FROM accs_shop WHERE phone IN (
                    SELECT phone FROM accs_shop LIMIT {amount}
                )
            """)
        return True
    except (Exception, asyncpg.PostgresError) as error:
        print("Error while moving accounts", error)
        return False


async def subtract_from_balance(user_id: int, amount: int) -> bool:
    try:
        query = """
            UPDATE subscriptions
            SET balance = balance - $1
            WHERE user_id = $2
                AND balance >= $1
        """
        await db.execute_query(query, amount, user_id)
        return True
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while subtracting from balance", error)
        return False


async def update_balance(user_id: int, operation: str, amount: int) -> None:
    """
    Updates the balance in the subscriptions table for the specified user_id.
    The operation can be either 'subtract' or 'multiply'.
    """
    try:
        if operation == 'subtract':
            await db.execute_query("""
                UPDATE subscriptions
                SET balance = balance - $1
                WHERE user_id = $2
            """, amount, user_id)
        elif operation == 'summ':
            await db.execute_query("""
                UPDATE subscriptions
                SET balance = balance + $1
                WHERE user_id = $2
            """, amount, user_id)
        else:
            raise ValueError("Invalid operation. Operation must be 'subtract' or 'summ'")
        logger.info(f"Balance updated for user_id: {user_id}")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while updating balance", error)