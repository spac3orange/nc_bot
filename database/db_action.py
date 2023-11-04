import sqlite3 as sq
from data.config_aiogram import config_aiogram
from data.logger import logger
import datetime
from typing import List, Dict, Union, Tuple


@logger.catch()
async def db_start() -> None:
    """
    Initializes the connection to the database and creates the tables if they do not exist.
    """
    global db, cur
    db = sq.connect('database/user_base.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS telegram_groups(group_name TEXT, group_id INTEGER, promts TEXT, "
                "triggers TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS telegram_accounts(phone TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS telegram_monitor_account(phone TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS gpt_accounts(api_key TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, user_name TEXT)")
    db.commit()
    logger.info('connected to database')


async def db_get_users() -> list:
    """
    Retrieves all information from the 'users' table and returns it as a list of tuples.
    """
    db = sq.connect('database/user_base.db')
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    db.close()
    return users

@logger.catch()
async def db_delete_user(user_name: str) -> None:
    """
    Deletes a user from the 'users' table based on user_id.
    """
    with sq.connect('database/user_base.db') as db:
        cur = db.cursor()
        cur.execute("DELETE FROM users WHERE user_name = ?", (user_name,))
        db.commit()
        logger.info(f"User with user_name {user_name} deleted from the table.")

async def db_add_user(user_id: int, user_name: str) -> None:
    """
    Adds a new user to the 'users' table if the user_id doesn't already exist.
    """
    with sq.connect('database/user_base.db') as db:
        cur = db.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        existing_user = cur.fetchone()
        if existing_user:
            logger.warning(f"User with user_id {user_id} already exists in the table.")
        else:
            cur.execute("INSERT INTO users (user_id, user_name) VALUES (?, ?)", (user_id, user_name))
            db.commit()
            logger.info(f"User with user_id {user_id} added to the table.")

async def db_get_all_data() -> dict:
    """
    Retrieves all data from all tables and returns it as a dictionary.
    """
    db = sq.connect('database/user_base.db')
    cur = db.cursor()

    data = {}

    # Retrieve data from telegram_groups table
    cur.execute("SELECT * FROM telegram_groups")
    groups_data = cur.fetchall()
    data['telegram_groups'] = groups_data

    # Retrieve data from telegram_accounts table
    cur.execute("SELECT * FROM telegram_accounts")
    accounts_data = cur.fetchall()
    data['telegram_accounts'] = accounts_data

    # Retrieve data from telegram_monitor_account table
    cur.execute("SELECT * FROM telegram_monitor_account")
    monitor_account_data = cur.fetchall()
    data['telegram_monitor_account'] = monitor_account_data

    # Retrieve data from gpt_accounts table
    cur.execute("SELECT * FROM gpt_accounts")
    gpt_accounts_data = cur.fetchall()
    data['gpt_accounts'] = gpt_accounts_data

    cur.close()
    db.close()

    return data


@logger.catch()
async def db_add_tg_account(phone_number: str) -> None:
    """
    Adds a Telegram account to the database.
    """
    global db, cur
    try:
        cur.execute("INSERT INTO telegram_accounts(phone) VALUES (?)", (phone_number,))
        db.commit()
        logger.info(f"Telegram account {phone_number} added to the database")
    except Exception as e:
        logger.error(f"Error adding Telegram account to the database: {e}")


@logger.catch()
async def db_add_tg_monitor_account(phone_number: str) -> None:
    """
    Adds or replaces a Telegram account in the database.
    """
    global db, cur
    try:
        cur.execute("REPLACE INTO telegram_monitor_account(phone) VALUES (?)", (phone_number,))
        db.commit()
        logger.info(f"Telegram account {phone_number} added or updated in the database")
    except Exception as e:
        logger.error(f"Error adding or updating Telegram account in the database: {e}")

@logger.catch()
async def db_remove_tg_account(phone_number: str) -> None:
    """
    Removes a Telegram account from the database.
    """
    global db, cur
    try:
        cur.execute("DELETE FROM telegram_accounts WHERE phone=?", (phone_number,))
        db.commit()
        logger.info(f"Telegram account {phone_number} removed from the database")
    except Exception as e:
        logger.error(f"Error removing Telegram account from the database: {e}")


@logger.catch()
async def db_get_all_tg_accounts() -> List[str]:
    """
    Retrieves all Telegram accounts from the database.
    """
    try:
        with sq.connect('database/user_base.db') as db:
            cur = db.cursor()
            cur.execute("SELECT phone FROM telegram_accounts")
            rows = cur.fetchall()
            phone_numbers = [row[0] for row in rows]
            return phone_numbers
    except Exception as e:
        logger.error(f"Error retrieving Telegram accounts from the database: {e}")
        return []


@logger.catch()
async def db_get_monitor_account() -> List[str]:
    """
    Retrieves all Telegram accounts from the database.
    """
    db = sq.connect('database/user_base.db')
    cur = db.cursor()
    try:
        cur.execute("SELECT phone FROM telegram_monitor_account")
        rows = cur.fetchall()
        phone_numbers = [row[0] for row in rows]
        return phone_numbers
    except Exception as e:
        logger.error(f"Error retrieving Telegram accounts from the database: {e}")
        return []


@logger.catch()
async def db_add_telegram_group(group_link: str, group_id: int) -> None:
    """
    Adds a Telegram group to the database with group_link and group_id.
    """
    global db, cur
    try:
        cur.execute("INSERT INTO telegram_groups(group_name, group_id) VALUES (?, ?)", (group_link, group_id))
        db.commit()
        logger.info(f"Telegram group {group_link} (ID: {group_id}) added to the database")
    except Exception as e:
        logger.error(f"Error adding Telegram group to the database: {e}")

@logger.catch()
async def db_remove_telegram_group(group_name: str) -> None:
    """
    Removes a Telegram group from the database.
    """
    global db, cur
    try:
        cur.execute("DELETE FROM telegram_groups WHERE group_name=?", (group_name,))
        db.commit()
        logger.info(f"Telegram group {group_name} removed from the database")
    except Exception as e:
        logger.error(f"Error removing Telegram group from the database: {e}")


@logger.catch()
async def db_get_all_telegram_groups() -> List[str]:
    """
    Retrieves a list of all Telegram groups from the database.
    """
    global db, cur
    try:
        cur.execute("SELECT group_name FROM telegram_groups")
        groups = cur.fetchall()
        group_list = [group[0] for group in groups]
        logger.info("Retrieved all Telegram groups from the database")
        return group_list
    except Exception as e:
        logger.error(f"Error retrieving Telegram groups from the database: {e}")
        return []

@logger.catch()
async def db_get_all_telegram_ids() -> List[str]:
    """
    Retrieves a list of all Telegram groups from the database.
    """
    global db, cur
    try:
        cur.execute("SELECT group_id FROM telegram_groups")
        groups = cur.fetchall()
        group_list = [group[0] for group in groups]
        logger.info("Retrieved all Telegram id's from the database")
        return group_list
    except Exception as e:
        logger.error(f"Error retrieving Telegram id's from the database: {e}")
        return []


@logger.catch()
async def db_get_all_telegram_grp_id() -> List[str]:
    """
    Retrieves a list of all Telegram groups from the database.
    """
    global db, cur
    try:
        cur.execute("SELECT group_id FROM telegram_groups")
        groups = cur.fetchall()
        group_list = [group[0] for group in groups]
        logger.info("Retrieved all Telegram groups from the database")
        return group_list
    except Exception as e:
        logger.error(f"Error retrieving Telegram groups from the database: {e}")
        return []


async def db_get_promts_for_group(group_name: str) -> str:
    """
    Retrieves the prompts for a specific Telegram group from the database.
    """
    try:
        with sq.connect('database/user_base.db') as db:
            cur = db.cursor()
            cur.execute("SELECT promts FROM telegram_groups WHERE group_name=?", (group_name,))
            result = cur.fetchone()
            if result:
                prompts = result[0]
                logger.info(f"Retrieved prompts for Telegram group {group_name} from the database")
                return prompts
            else:
                logger.info(f"No prompts found for Telegram group {group_name} in the database")
                return ""
    except Exception as e:
        logger.error(f"Error retrieving prompts for Telegram group from the database: {e}")
        return ""

@logger.catch()
async def db_add_promts_for_group(group_name: str, promts: str) -> bool:
    """
    Adds promts for a specific Telegram group to the database.
    """
    global db, cur
    try:
        cur.execute("UPDATE telegram_groups SET promts=? WHERE group_name=?", (promts, group_name))
        db.commit()
        logger.info(f"Promts added for Telegram group {group_name} in the database")
        return True
    except Exception as e:
        logger.error(f"Error adding promts for Telegram group to the database: {e}")
        return False


@logger.catch()
async def db_add_trigger_for_group(group_name: str, triggers: List[str]) -> bool:
    """
    Adds triggers for a specific Telegram group to the database.
    """
    global db, cur
    try:
        cur.execute("SELECT triggers FROM telegram_groups WHERE group_name=?", (group_name,))
        result = cur.fetchone()
        if result:
            existing_triggers = result[0]
            if existing_triggers:
                existing_triggers = existing_triggers.strip()  # Удаляем пробелы в начале и конце строки
                existing_triggers += "\n" + "\n".join(triggers)  # Добавляем новые триггеры с новой строки
            else:
                existing_triggers = "\n".join(triggers)  # Используем только новые триггеры
            cur.execute("UPDATE telegram_groups SET triggers=? WHERE group_name=?", (existing_triggers, group_name))
            db.commit()
            logger.info(f"Triggers added for Telegram group {group_name} in the database")
            return True
        else:
            logger.info(f"No triggers found for Telegram group {group_name} in the database")
            return False
    except Exception as e:
        logger.error(f"Error adding triggers for Telegram group to the database: {e}")
        return False

@logger.catch()
async def db_get_triggers_for_group(group_name: str) -> str:
    """
    Retrieves all triggers for a specific Telegram group from the database.
    """
    global db, cur
    try:
        cur.execute("SELECT triggers FROM telegram_groups WHERE group_name=?", (group_name,))
        result = cur.fetchone()
        if result:
            triggers = result[0]
            logger.info(f"Retrieved triggers for Telegram group {group_name} from the database")
            return triggers
        else:
            logger.info(f"No triggers found for Telegram group {group_name} in the database")
            return ""
    except Exception as e:
        logger.error(f"Error retrieving triggers for Telegram group from the database: {e}")
        return ""


@logger.catch()
async def db_remove_triggers_for_group(group_name: str, triggers: List[str]) -> bool:
    """
    Removes triggers for a specific Telegram group from the database.
    """
    global db, cur
    try:
        cur.execute("SELECT triggers FROM telegram_groups WHERE group_name=?", (group_name,))
        result = cur.fetchone()
        if result:
            existing_triggers = result[0].split("\n")  # Разделяем существующие триггеры по строкам
            updated_triggers = [trigger for trigger in existing_triggers if trigger not in triggers]  # Удаляем указанные триггеры
            updated_triggers_str = "\n".join(updated_triggers)  # Объединяем триггеры обратно в одну строку
            cur.execute("UPDATE telegram_groups SET triggers=? WHERE group_name=?", (updated_triggers_str, group_name))
            db.commit()
            logger.info(f"Triggers removed for Telegram group {group_name} from the database")
            return True
        else:
            logger.info(f"No triggers found for Telegram group {group_name} in the database")
            return False
    except Exception as e:
        logger.error(f"Error removing triggers for Telegram group from the database: {e}")
        return False


@logger.catch()
async def get_groups_and_triggers() -> Dict[str, str]:
    """
    Retrieves all groups and their triggers from the database.
    Returns a dictionary where keys are group names and values are triggers as a comma-separated string.
    """
    db = sq.connect('database/user_base.db')
    cur = db.cursor()
    try:
        cur.execute("SELECT group_name, triggers FROM telegram_groups")
        rows = cur.fetchall()
        groups_triggers_dict = {}
        for row in rows:
            print(row)
            group_name, triggers = row
            triggers_str = triggers.replace("\n", ", ")  # Заменяем переносы строк на запятые
            groups_triggers_dict[group_name] = triggers_str
        logger.info("Retrieved all groups and triggers from the database")
        return groups_triggers_dict
    except Exception as e:
        logger.error(f"Error retrieving groups and triggers from the database: {e}")
        return {}


@logger.catch()
async def db_add_gpt_account(api_key: str) -> None:
    """
    Adds a GPT account to the database.
    """
    global db, cur
    try:
        cur.execute("INSERT INTO gpt_accounts(api_key) VALUES (?)", (api_key,))
        db.commit()
        logger.info(f"GPT account with API key {api_key} added to the database")
    except Exception as e:
        logger.error(f"Error adding GPT account to the database: {e}")



@logger.catch()
async def db_remove_gpt_account(api_key: str) -> None:
    """
    Removes a GPT account from the database.
    """
    global db, cur
    try:
        cur.execute("DELETE FROM gpt_accounts WHERE api_key=?", (api_key,))
        db.commit()
        logger.info(f"GPT account {api_key} removed from the database")
    except Exception as e:
        logger.error(f"Error removing GPT account from the database: {e}")


async def db_get_all_gpt_accounts() -> List[str]:
    """
    Returns a list of all API keys from the gpt_accounts table.
    """
    try:
        with sq.connect('database/user_base.db') as db:
            cur = db.cursor()
            cur.execute("SELECT api_key FROM gpt_accounts")
            rows = cur.fetchall()
            api_keys = [row[0] for row in rows]
            logger.info("Retrieved all GPT account API keys from the database")
            return api_keys
    except Exception as e:
        logger.error(f"Error retrieving GPT account API keys from the database: {e}")
        return []