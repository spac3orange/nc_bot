from typing import List, Dict
import asyncpg
from data import logger
from .db_action import db


async def db_add_tg_account(phone_number: str, sex='Мужской') -> None:
    """
    Adds a Telegram account to the database.
    """
    try:

        query = "INSERT INTO telegram_accounts(phone, sex) VALUES ($1, $2)"
        await db.execute_query(query, phone_number, sex)
        logger.info(f"Telegram account {phone_number} added to the database")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error adding Telegram account to the database: {error}")


async def db_add_tg_monitor_account(phone_number: str) -> None:
    """
    Adds or replaces a Telegram account in the database.
    """
    try:

        query = "INSERT INTO telegram_monitor_account(phone) VALUES ($1) ON CONFLICT (phone) DO UPDATE SET phone = $1"
        await db.execute_query(query, phone_number)
        logger.info(f"Telegram account {phone_number} added or updated in the database")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error adding or updating Telegram account in the database: {error}")


async def db_remove_tg_account(phone_number: str) -> None:
    """
    Removes a Telegram account from the database.
    """
    try:

        query = "DELETE FROM telegram_accounts WHERE phone = $1"
        await db.execute_query(query, phone_number)
        logger.info(f"Telegram account {phone_number} removed from the database")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error removing Telegram account from the database: {error}")


async def db_get_all_tg_accounts(free_accs=True) -> List[str]:
    """
    Retrieves all Telegram accounts from the database.
    """
    try:
        if free_accs:
            query = "SELECT phone FROM telegram_accounts"
            rows = await db.fetch_all(query)
            phone_numbers = [row[0] for row in rows]
            return phone_numbers
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving Telegram accounts from the database: {error}")
        return []


async def db_get_monitor_account() -> List[str]:
    """
    Retrieves all Telegram accounts from the database.
    """
    try:

        query = "SELECT phone FROM telegram_monitor_account"
        rows = await db.fetch_all(query)
        phone_numbers = [row[0] for row in rows]
        return phone_numbers
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving Telegram accounts from the database: {error}")
        return []


async def move_accounts(user_id: int, num_accounts: int) -> None:
    try:
        # Проверить существование таблицы accounts_{user_id}
        query_check_table = f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'accounts_{user_id}')"
        table_exists = await db.execute_query_return(query_check_table)
        if not table_exists[0][0]:
            # Создать таблицу accounts_{user_id}, если она не существует
            table_name = f"accounts_{user_id}"
            query = f"""
                            CREATE TABLE IF NOT EXISTS {table_name} (
                                phone TEXT PRIMARY KEY,
                                comments INTEGER DEFAULT 0,
                                comments_today INTEGER DEFAULT 0,
                                sex TEXT DEFAULT 'Мужской',
                                status TEXT DEFAULT 'Active',
                                in_work BOOLEAN DEFAULT False
                            )
                        """
            await db.execute_query(query)

        # Получить список аккаунтов для перемещения
        query_select = "SELECT phone, sex FROM telegram_accounts LIMIT $1"
        accounts_to_move = await db.execute_query_return(query_select, num_accounts)

        # Переместить аккаунты в таблицу accounts_{user_id}
        query_insert = f"INSERT INTO accounts_{user_id} (phone, sex) VALUES ($1, $2)"
        for account in accounts_to_move:
            phone = account["phone"]
            sex = account["sex"]
            await db.execute_query(query_insert, phone, sex)

        # Удалить перемещенные аккаунты из таблицы telegram_accounts
        query_delete = "DELETE FROM telegram_accounts WHERE phone IN (SELECT phone FROM telegram_accounts LIMIT $1)"
        await db.execute_query(query_delete, num_accounts)

        logger.info(f"Moved {num_accounts} accounts to accounts_{user_id}")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error moving accounts to accounts_{user_id}: {error}")


async def return_accounts(user_id):
    try:
        accounts = await db.fetch_all(f"SELECT phone, sex FROM accounts_{user_id}")
        if accounts:
            for account in accounts:
                phone = account['phone']
                sex = account['sex']
                await db.execute_query("INSERT INTO telegram_accounts (phone, sex) VALUES ($1, $2)", phone, sex)
            await db.execute_query(f"DROP TABLE IF EXISTS accounts_{user_id}")
            logger.info(f"All accounts from accounts_{user_id} table transferred to telegram_accounts table")
        else:
            logger.warning(f"No accounts found in accounts_{user_id} table")
    except Exception as e:
        logger.error(f"Error transferring accounts: {e}")

# ___________________________________________________
    # user_accs_table


async def create_user_accounts_table(user_id: int) -> None:
    """
    Creates a new table in the database with the name "settings_{user_id}" and the specified columns.

    """
    table_name = f"accounts_{user_id}"
    try:
        query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                phone TEXT PRIMARY KEY,
                comments INTEGER DEFAULT 0,
                comments_today INTEGER DEFAULT 0,
                sex TEXT DEFAULT 'Мужской',
                status TEXT DEFAULT 'Active',
                in_work BOOLEAN DEFAULT FALSE
            )
        """
        await db.execute_query(query)
        logger.info(f"Created table {table_name} in the database")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error while creating table {table_name}: {error}")


async def get_all_paid_accounts() -> Dict[str, List[str]]:
    """
    Retrieves all phone records from tables starting with "accounts_" and returns a dictionary of records.
    """
    try:
        query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'accounts_%'"
        table_names = await db.fetch_all(query)
        phone_records = {}
        for table_name in table_names:
            query = f"SELECT phone FROM {table_name['table_name']}"
            records = await db.fetch_all(query)
            phone_records[table_name['table_name']] = [record['phone'] for record in records]
        return phone_records
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while retrieving phone records from tables", error)
        return {}


async def get_user_accounts(user_id: int) -> List[str]:
    """
    Retrieves all phone numbers from the specified user's accounts table.

    """
    table_name = f"accounts_{user_id}"
    try:
        query = f"SELECT phone FROM {table_name}"
        rows = await db.fetch_all(query)
        phone_numbers = [row[0] for row in rows]
        logger.info(f"Retrieved phone numbers from table {table_name}")
        return phone_numbers
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving phone numbers from table {table_name}: {error}")
        return []


async def db_get_all_tg_accounts_with_comments(free_accs=True) -> dict:
    """
    Retrieves all Telegram accounts from the database, including tables starting with "accounts_".
    Returns a dictionary where the keys are table names and the values are dictionaries with "phone" and "comments" values.
    """
    try:
        result = {}

        # Retrieve information from the "telegram_accounts" table
        if free_accs:
            query = "SELECT phone, comments, sex FROM telegram_accounts"
            rows = await db.fetch_all(query)
            accounts = [{"phone": row[0], "comments": row[1], "sex": row[2]} for row in rows]
            result["telegram_accounts"] = accounts

        # Retrieve information from tables starting with "accounts_"
        query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'accounts_%'"
        rows = await db.fetch_all(query)
        table_names = [row[0] for row in rows]
        if table_names:
            for table_name in table_names:
                query = f"SELECT phone, comments, sex FROM {table_name}"
                rows = await db.fetch_all(query)
                if not rows:  # Skip the table if it's empty
                    continue
                accounts = [{"phone": row[0], "comments": row[1], "sex": row[2]} for row in rows]
                result[table_name] = accounts

        return result
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving Telegram accounts with comments from the database: {error}")
        return {}


async def increment_comments(table_name: str, phone: str) -> None:
    try:
        query = f"UPDATE {table_name} SET comments = comments + 1, comments_today = comments_today + 1 WHERE phone = $1"
        await db.execute_query(query, phone)
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error incrementing comments for phone {phone} in table {table_name}: {error}")


async def get_phones_with_comments_today_less_than(table_name: str, max_comments: int) -> List[str]:
    try:
        query = f"SELECT phone FROM {table_name} WHERE comments_today < $1 AND in_work = False AND status = 'Active'"
        rows = await db.execute_query_return(query, max_comments)
        phones = [row[0] for row in rows]
        return phones
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving phones with comments_today less than {max_comments} from table {table_name}: {error}")
        return []


async def reset_comments_today() -> None:
    try:
        # Reset comments_today in telegram_accounts table
        await db.execute_query("UPDATE telegram_accounts SET comments_today = 0")

        # Get all table names starting with 'accounts_'
        query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'accounts_%'"
        rows = await db.execute_query_return(query)

        if rows:
            table_names = [row[0] for row in rows]

            # Reset comments_today in each accounts_ table
            for table_name in table_names:
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                count = await db.execute_query_return(count_query)

                if count and count[0][0] > 0:
                    await db.execute_query(f"UPDATE {table_name} SET comments_today = 0")

        logger.info("Reset comments_today in telegram_accounts and accounts_ tables")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error resetting comments_today: {error}")


async def get_sex_by_phone(phone: str, uid=False) -> str:
    """
    Retrieves the value from the 'sex' column for the given phone number from the 'telegram_accounts' table.
    Returns the value of 'sex' column as a string.
    """
    try:
        if uid:
            result = await db.execute_query_return(f"SELECT sex FROM accounts_{uid} WHERE phone = $1", phone)
        else:
            result = await db.execute_query_return("SELECT sex FROM telegram_accounts WHERE phone = $1", phone)
        if result:
            sex = result[0][0]
            return sex
        else:
            logger.info('Phone number not found in the table')
            return None
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while retrieving sex from the table", error)
        return None


async def update_user_account_sex(user_id: int, phone: str, sex: str) -> None:
    table_name = f"accounts_{user_id}"
    try:
        query = f"""
            UPDATE {table_name}
            SET sex = $1
            WHERE phone = $2
        """
        await db.execute_query(query, sex, phone)
        logger.info(f"Updated sex for account {phone} in table {table_name}")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error while updating sex for account {phone} in table {table_name}: {error}")


async def set_in_work(table_name: str, phone: str, stop_work: bool = False) -> None:
    try:
        value = "True" if not stop_work else "False"
        query = f"UPDATE {table_name} SET in_work = {value} WHERE phone = $1"
        await db.execute_query(query, phone)
    except (Exception, asyncpg.PostgresError) as error:
        action = "True" if not stop_work else "False"
        logger.error(f"Error setting in_work={action} for phone {phone} in table {table_name}: {error}")


async def change_acc_status(phone, status, table_name):
    try:
        query = f"UPDATE {table_name} SET status = {status} WHERE phone = $1"
        await db.execute_query(query, phone)
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error setting status={status} for phone {phone} in table {table_name}: {error}")


async def get_extra_accounts(user_id: int) -> List[str]:
    try:
        async with db.pool.acquire() as conn:
            query = f"SELECT phone FROM extra_accounts_{user_id}"
            rows = await conn.fetch(query)
            phone_numbers = [row['phone'] for row in rows]
            return phone_numbers
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving extra accounts for user {user_id}: {error}")
        return []


async def get_in_work_status(phone: str, table_name: str) -> bool:
    try:
        query = f"""
            SELECT in_work
            FROM {table_name}
            WHERE phone = $1
        """
        result = await db.execute_query(query, phone)
        if result:
            logger.info(f"Retrieved in_work status for phone {phone} in table {table_name}")
            return result[0]['in_work']
        else:
            logger.warning(f"No in_work status found for phone {phone} in table {table_name}")
            return False
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error while retrieving in_work status for phone {phone} in table {table_name}: {error}")
        return False