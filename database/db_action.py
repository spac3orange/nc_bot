import asyncpg
from environs import Env
from data import logger
from typing import List, Dict, Tuple
import asyncio

class Database:
    def __init__(self):
        self.env = Env()
        self.env.read_env(path='data/.env')
        self.user = self.env.str('DB_USER')
        self.password = self.env.str('DB_PASSWORD')
        self.host = self.env.str('DB_HOST')
        self.db_name = self.env.str('DB_NAME')
        self.db_port = self.env.str('DB_PORT')
        self.pool = None
        self.lock = asyncio.Lock()

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.db_name,
                port=self.db_port,
                min_size=20,
                max_size=100,
            )

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while creating connection pool", error)
            print(error)

    async def close_pool(self):
        if self.pool:
            await self.pool.close()

    async def execute_query(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)

    async def execute_query_return(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetch(query, *args)
                return result
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)
            return []

    async def fetch_row(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while fetching row", error)

    async def fetch_all(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while fetching all", error)

    async def db_start(self) -> None:
        """
        Initializes the connection to the database and creates the tables if they do not exist.
        """
        try:
            await self.create_pool()

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS telegram_channels (
                    user_id BIGINT,
                    channel_name TEXT,
                    channel_id BIGINT,
                    promts TEXT DEFAULT 'Нет',
                    triggers TEXT DEFAULT 'Нет',
                    group_link TEXT,
                    PRIMARY KEY (user_id, channel_id)
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS telegram_accounts (
                    phone TEXT PRIMARY KEY,
                    comments INTEGER DEFAULT 0,
                    comments_today INTEGER DEFAULT 0,
                    sex TEXT,
                    status TEXT DEFAULT 'Active',
                    in_work BOOLEAN DEFAULT FALSE
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS telegram_monitor_account (
                    phone TEXT PRIMARY KEY
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS gpt_accounts (
                    api_key TEXT PRIMARY KEY
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    user_name TEXT,
                    monitoring_status BOOLEAN DEFAULT FALSE,
                    notifications BOOLEAN DEFAULT TRUE
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    user_id BIGINT PRIMARY KEY,
                    sub_start_date TEXT,
                    sub_end_date TEXT,
                    sub_type TEXT DEFAULT 'DEMO',
                    sub_status BOOLEAN DEFAULT FALSE,
                    balance INTEGER DEFAULT 0,
                    comments_sent INTEGER DEFAULT 0
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS users_today (
                    user_id BIGINT PRIMARY KEY,
                    user_name TEXT
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS default_prompts (
                    prompt_text TEXT PRIMARY KEY
                )
            """)

            logger.info('connected to database')

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while connecting to DB", error)



    async def add_user_to_subscriptions(self, user_id: int) -> None:
        """
        Adds a user to the 'subscriptions' table if the user_id doesn't already exist.
        """
        try:
            query = "SELECT user_id FROM subscriptions WHERE user_id = $1"
            existing_user = await self.fetch_row(query, user_id)

            if existing_user:
                logger.warning(f"User with user_id {user_id} already exists in the subscriptions table.")
            else:
                query = "INSERT INTO subscriptions (user_id) VALUES ($1)"
                await self.execute_query(query, user_id)
                logger.info(f"User with user_id {user_id} added to the subscriptions table.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while adding user with user_id {user_id} to the subscriptions table.", error)

    async def db_get_users(self) -> list:
        """
        Retrieves all information from the 'users' table and returns it as a list of tuples.
        """
        try:
            query = "SELECT * FROM users"
            users = await self.fetch_all(query)
            return users
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving users from DB", error)
            return []

    async def db_get_users_today(self) -> list:
        """
        Retrieves all information from the 'users' table and returns it as a list of tuples.
        """
        try:
            query = "SELECT * FROM users_today"
            users = await self.fetch_all(query)
            return users
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving users from DB", error)
            return []

    async def db_add_user_today(self, user_id: int, user_name: str) -> None:
        """
        Adds a new user to the 'users' table if the user_id doesn't already exist.
        """
        try:
            query = "SELECT user_id FROM users_today WHERE user_id = $1"
            existing_user = await self.fetch_row(query, user_id)

            if existing_user:
                logger.warning(f"User with user_id {user_id} already exists in the table users_today.")
            else:
                query = "INSERT INTO users_today (user_id, user_name) VALUES ($1, $2)"
                await self.execute_query(query, user_id, user_name)
                logger.info(f"User with user_id {user_id} added to the table users_today.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while adding user with user_id {user_id} to the table users_today.", error)

    async def clear_users_today(self) -> None:
        """
        Clears the 'users_today' table by deleting all records.
        """
        try:
            query = "DELETE FROM users_today"
            await self.execute_query(query)
            logger.info("Cleared 'users_today' table")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while clearing 'users_today' table", error)

    async def get_monitoring_user_ids(self) -> List[int]:
        """
        Retrieves a list of all user_ids from the table where monitoring_status is True.
        """
        try:
            query = "SELECT user_id FROM users WHERE monitoring_status = TRUE"
            rows = await self.fetch_all(query)
            user_ids = [row[0] for row in rows]
            logger.info("Retrieved user_ids with monitoring_status True from the database")
            return user_ids
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving user_ids with monitoring_status True from the database: {error}")
            return []

    async def db_delete_user(self, user_name: str) -> None:
        """
        Deletes a user from the 'users' table based on user_name.
        """
        try:
            query = "DELETE FROM users WHERE user_name = $1"
            await self.execute_query(query, user_name)
            logger.info(f"User with user_name {user_name} deleted from the table.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while deleting user with user_name {user_name} from the table.", error)

    async def db_add_user(self, user_id: int, user_name: str) -> None:
        """
        Adds a new user to the 'users' table if the user_id doesn't already exist.
        """
        try:
            query = "SELECT user_id FROM users WHERE user_id = $1"
            existing_user = await self.fetch_row(query, user_id)

            if existing_user:
                logger.warning(f"User with user_id {user_id} already exists in the table.")
            else:
                query = "INSERT INTO users (user_id, user_name) VALUES ($1, $2)"
                await self.execute_query(query, user_id, user_name)
                logger.info(f"User with user_id {user_id} added to the table.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while adding user with user_id {user_id} to the table.", error)

    async def db_get_all_data(self) -> dict:
        """
        Retrieves all data from all tables and returns it as a dictionary.
        """
        try:
            
            data = {}
            # Retrieve data from telegram_groups table
            query = "SELECT * FROM telegram_channels"
            groups_data = await self.fetch_all(query)
            data['telegram_channels'] = groups_data
            # Retrieve data from telegram_accounts table
            query = "SELECT * FROM telegram_accounts"
            accounts_data = await self.fetch_all(query)
            data['telegram_accounts'] = accounts_data
            # Retrieve data from telegram_monitor_account table
            query = "SELECT * FROM telegram_monitor_account"
            monitor_account_data = await self.fetch_all(query)
            data['telegram_monitor_account'] = monitor_account_data
            # Retrieve data from gpt_accounts table
            query = "SELECT * FROM gpt_accounts"
            gpt_accounts_data = await self.fetch_all(query)
            data['gpt_accounts'] = gpt_accounts_data

            return data
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving data from tables", error)
            return {}
        

    async def db_add_tg_account(self, phone_number: str, sex='Мужской') -> None:
        """
        Adds a Telegram account to the database.
        """
        try:
            
            query = "INSERT INTO telegram_accounts(phone, sex) VALUES ($1, $2)"
            await self.execute_query(query, phone_number, sex)
            logger.info(f"Telegram account {phone_number} added to the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error adding Telegram account to the database: {error}")
        

    async def db_add_tg_monitor_account(self, phone_number: str) -> None:
        """
        Adds or replaces a Telegram account in the database.
        """
        try:
            
            query = "INSERT INTO telegram_monitor_account(phone) VALUES ($1) ON CONFLICT (phone) DO UPDATE SET phone = $1"
            await self.execute_query(query, phone_number)
            logger.info(f"Telegram account {phone_number} added or updated in the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error adding or updating Telegram account in the database: {error}")
        

    async def db_remove_tg_account(self, phone_number: str) -> None:
        """
        Removes a Telegram account from the database.
        """
        try:
            
            query = "DELETE FROM telegram_accounts WHERE phone = $1"
            await self.execute_query(query, phone_number)
            logger.info(f"Telegram account {phone_number} removed from the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error removing Telegram account from the database: {error}")
        

    async def db_get_all_tg_accounts(self, free_accs=True) -> List[str]:
        """
        Retrieves all Telegram accounts from the database.
        """
        try:
            if free_accs:
                
                query = "SELECT phone FROM telegram_accounts"
                rows = await self.fetch_all(query)
                phone_numbers = [row[0] for row in rows]
                return phone_numbers
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram accounts from the database: {error}")
            return []
        

    async def db_get_monitor_account(self) -> List[str]:
        """
        Retrieves all Telegram accounts from the database.
        """
        try:
            
            query = "SELECT phone FROM telegram_monitor_account"
            rows = await self.fetch_all(query)
            phone_numbers = [row[0] for row in rows]
            return phone_numbers
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram accounts from the database: {error}")
            return []
        

    async def db_add_telegram_group(self, uid, channel_link: str, channel_id: int, group_link: str) -> None:
        """
        Adds a Telegram group to the database with group_link and group_id.
        """
        try:
            
            query = "INSERT INTO telegram_channels(user_id, channel_name, channel_id, group_link) VALUES ($1, $2, $3, $4)"
            await self.execute_query(query, uid, channel_link, channel_id, group_link)
            logger.info(f"Telegram channel {channel_link} (ID: {channel_id}) discussion_group: {group_link} added to the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error adding Telegram group to the database: {error}")
        

    async def db_remove_telegram_group(self, group_name: str) -> None:
        """
        Removes a Telegram group from the database.
        """
        try:
            
            query = "DELETE FROM telegram_channels WHERE channel_name = $1"
            await self.execute_query(query, group_name)
            logger.info(f"Telegram channel {group_name} removed from the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error removing Telegram channel from the database: {error}")
        

    async def db_get_all_telegram_channels(self, user_id: int) -> List[str]:
        """
        Retrieves a list of all Telegram channels from the database for a given user_id.
        """
        try:
            
            query = "SELECT channel_name FROM telegram_channels WHERE user_id = $1"
            channels = await self.fetch_all(query, user_id)
            channel_list = [channel[0] for channel in channels]
            logger.info(f"Retrieved all Telegram channels from the database for user_id: {user_id}")
            return channel_list
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram channels from the database for user_id: {user_id}: {error}")
            return []

    async def db_get_all_telegram_groups(self, user_id: int) -> List[str]:
        """
        Retrieves a list of all Telegram group links from the database for a given user_id.
        """
        try:
            query = "SELECT group_link FROM telegram_channels WHERE user_id = $1"
            channels = await self.fetch_all(query, user_id)
            channel_list = [channel[0] for channel in channels]
            logger.info(f"Retrieved all Telegram group links from the database for user_id: {user_id}")
            return channel_list
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram group links from the database for user_id: {user_id}: {error}")
            return []

    async def db_get_group_link_by_channel_name(self, channel_name: int) -> str:
        """
        Retrieves the group_link from the database based on the channel_id.
        """
        try:
            query = "SELECT group_link FROM telegram_channels WHERE channel_name = $1"
            result = await self.fetch_row(query, channel_name)
            if result:
                group_link = result[0]
                logger.info(f"Retrieved group_link from the database for channel_name: {channel_name}")
                return group_link
            else:
                logger.warning(f"No group_link found in the database for channel_name: {channel_name}")
                return ""
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving group_link from the database for channel_name: {channel_name}: {error}")
            return ""


    async def db_get_all_telegram_ids(self, user_id: int) -> List[str]:
        """
        Retrieves a list of all Telegram channel_ids from the database for a given user_id.
        """
        try:
            
            query = "SELECT channel_id FROM telegram_channels WHERE user_id = $1"
            ids = await self.fetch_all(query, user_id)
            id_list = [id[0] for id in ids]
            logger.info(f"Retrieved all Telegram channel_ids from the database for user_id: {user_id}")
            return id_list
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram channel_ids from the database for user_id: {user_id}: {error}")
            return []


    async def db_get_all_telegram_grp_id(self) -> List[str]:
        """
        Retrieves a list of all Telegram groups from the database.
        """
        try:

            query = "SELECT channel_id FROM telegram_channels"
            groups = await self.fetch_all(query)
            group_list = [group[0] for group in groups]
            logger.info("Retrieved all Telegram channels from the database")
            return group_list
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram channels from the database: {error}")
            return []


    async def db_get_promts_for_group(self, group_name: str) -> str:
        """
        Retrieves the prompts for a specific Telegram group from the database.
        """
        try:
            
            query = "SELECT promts FROM telegram_channels WHERE channel_name = $1"
            result = await self.fetch_row(query, group_name)
            if result:
                prompts = result[0]
                logger.info(f"Retrieved prompts for Telegram channel {group_name} from the database")
                return prompts
            else:
                logger.info(f"No prompts found for Telegram channel {group_name} in the database")
                return ""
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving prompts for Telegram channel from the database: {error}")
            return ""

    async def db_get_all_promts(self) -> Dict[str, str]:
        """
        Retrieves the prompts for all Telegram groups from the database.
        """
        try:
            query = "SELECT channel_name, promts FROM telegram_channels"
            results = await self.fetch_all(query)
            prompts_dict = {result[0]: result[1] for result in results}
            logger.info("Retrieved prompts for all Telegram channels from the database")
            return prompts_dict
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving prompts for Telegram channels from the database: {error}")
            return {}


    async def db_add_promts_for_group(self, group_name: str, promts: str) -> bool:
        """
        Adds promts for a specific Telegram group to the database.
        """
        try:
            
            query = "UPDATE telegram_channels SET promts = $1 WHERE channel_name = $2"
            await self.execute_query(query, promts, group_name)
            logger.info(f"Prompts added for Telegram group {group_name} in the database")
            return True
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error adding prompts for Telegram group to the database: {error}")
            return False
        

    async def db_add_trigger_for_group(self, group_name: str, triggers: List[str]) -> bool:
        """
        Adds triggers for a specific Telegram group to the database.
        """
        try:
            
            query = "SELECT triggers FROM telegram_channels WHERE channel_name = $1"
            existing_triggers = await self.fetch_row(query, group_name)

            if existing_triggers:
                existing_triggers = existing_triggers[0]
                if existing_triggers:
                    existing_triggers = existing_triggers.strip()  # Удаляем пробелы в начале и конце строки
                    existing_triggers += "\n" + "\n".join(triggers)  # Добавляем новые триггеры с новой строки
                else:
                    existing_triggers = "\n".join(triggers)  # Используем только новые триггеры
                query = "UPDATE telegram_channels SET triggers = $1 WHERE channel_name = $2"
                await self.execute_query(query, existing_triggers, group_name)
                logger.info(f"Triggers added for Telegram group {group_name} in the database")
                return True
            else:
                logger.info(f"No triggers found for Telegram group {group_name} in the database")
                return False
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error adding triggers for Telegram group to the database: {error}")
            return False
        

    async def db_get_triggers_for_group(self, group_name: str) -> str:
        """
        Retrieves all triggers for a specific Telegram group from the database.
        """
        try:
            
            query = "SELECT triggers FROM telegram_channels WHERE channel_name = $1"
            result = await self.fetch_row(query, group_name)

            if result:
                triggers = result[0]
                logger.info(f"Retrieved triggers for Telegram group {group_name} from the database")
                return triggers
            else:
                logger.info(f"No triggers found for Telegram group {group_name} in the database")
                return ""
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving triggers for Telegram group from the database: {error}")
            return ""
        

    async def db_remove_triggers_for_group(self, group_name: str, triggers: List[str]) -> bool:
        """
        Removes triggers for a specific Telegram group from the database.
        """
        try:
            
            query = "SELECT triggers FROM telegram_channels WHERE group_name = $1"
            result = await self.fetch_row(query, group_name)

            if result:
                existing_triggers = result[0].split("\n")
                updated_triggers = [trigger for trigger in existing_triggers if trigger not in triggers]
                updated_triggers_str = "\n".join(updated_triggers)

                query = "UPDATE telegram_channels SET triggers = $1 WHERE group_name = $2"
                await self.execute_query(query, updated_triggers_str, group_name)

                logger.info(f"Triggers removed for Telegram group {group_name} from the database")
                return True
            else:
                logger.info(f"No triggers found for Telegram group {group_name} in the database")
                return False
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error removing triggers for Telegram group from the database: {error}")
            return False
        

    async def get_user_groups_and_triggers(self, user_id: int) -> Dict[int, Dict[Tuple[str, str], str]]:
        """
        Retrieves all groups and their triggers from the database for a given user_id.
        Returns a dictionary where keys are user ids, and values are dictionaries where keys are tuples of channel_name and channel_id, and values are triggers.
        """
        try:
            
            query = "SELECT channel_name, channel_id, triggers FROM telegram_channels WHERE user_id = $1"
            rows = await self.fetch_all(query, user_id)
            user_groups_triggers_dict = {}
            for row in rows:
                channel_name, channel_id, triggers = row
                triggers_str = triggers.replace("\n", ", ")  # Заменяем переносы строк на запятые
                channel_tuple = (channel_name, channel_id)
                if user_id not in user_groups_triggers_dict:
                    user_groups_triggers_dict[user_id] = {}
                user_groups_triggers_dict[user_id][channel_tuple] = triggers_str
            logger.info(f"Retrieved all channels and triggers from the database for user_id: {user_id}")
            return user_groups_triggers_dict
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving channels and triggers from the database for user_id: {user_id}: {error}")
            return {}
        

    async def db_add_gpt_account(self, api_key: str) -> None:
        """
        Adds a GPT account to the database.
        """
        try:
            
            query = "INSERT INTO gpt_accounts(api_key) VALUES ($1)"
            await self.execute_query(query, api_key)
            logger.info(f"GPT account with API key {api_key} added to the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error adding GPT account to the database: {error}")
        

    async def db_remove_gpt_account(self, api_key: str) -> None:
        """
        Removes a GPT account from the database.
        """
        try:
            
            query = "DELETE FROM gpt_accounts WHERE api_key = $1"
            await self.execute_query(query, api_key)
            logger.info(f"GPT account {api_key} removed from the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error removing GPT account from the database: {error}")
        

    async def db_get_all_gpt_accounts(self) -> List[str]:
        """
        Returns a list of all API keys from the gpt_accounts table.
        """
        try:
            
            query = "SELECT api_key FROM gpt_accounts"
            rows = await self.fetch_all(query)
            api_keys = [row[0] for row in rows]
            logger.info("Retrieved all GPT account API keys from the database")
            return api_keys
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving GPT account API keys from the database: {error}")
            return []
        

    async def get_user_info(self, uid):
        try:
            user_info = {}

            # Получение информации из таблицы users
            user_row = await self.fetch_row("SELECT * FROM users WHERE user_id = $1", uid)
            if user_row:
                user_info["user_id"] = user_row["user_id"]
                user_info["user_name"] = user_row["user_name"]

            # Получение информации из таблицы subscriptions
            subscription_row = await self.fetch_row("SELECT * FROM subscriptions WHERE user_id = $1", uid)
            if subscription_row:
                user_info["sub_start_date"] = subscription_row["sub_start_date"]
                user_info["sub_end_date"] = subscription_row["sub_end_date"]
                user_info["sub_type"] = subscription_row["sub_type"]
                user_info["sub_status"] = subscription_row["sub_status"]
                user_info["balance"] = subscription_row["balance"]
                user_info["comments_sent"] = subscription_row["comments_sent"]

            return user_info

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving user info", error)
            print(error)


    async def toggle_monitoring_status(self, user_id: int, status: bool) -> None:
        """
        Toggles the monitoring_status for a given user_id in the users table.
        """
        try:
            
            query = "UPDATE users SET monitoring_status = $1 WHERE user_id = $2"
            await self.execute_query(query, status, user_id)
            logger.info(f"Monitoring status toggled to {status} for user_id: {user_id}")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error toggling monitoring status for user_id: {user_id}: {error}")
        

    async def get_monitoring_status(self, user_id: int) -> bool:
        """
        Retrieves the monitoring_status value for a given user_id from the users table.
        """
        try:
            
            query = "SELECT monitoring_status FROM users WHERE user_id = $1"
            row = await self.fetch_row(query, user_id)
            if row:
                monitoring_status = row[0]
                logger.info(f"Retrieved monitoring_status {monitoring_status} for user_id: {user_id}")
                return monitoring_status
            else:
                logger.info(f"No monitoring_status found for user_id: {user_id}")
                return False
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving monitoring_status for user_id: {user_id}: {error}")
            return False

    async def create_user_settings_table(self, user_id: int) -> None:
        """
        Creates a new table in the database with the name "settings_{user_id}" and the specified columns.
        """
        try:
            table_name = f"settings_{user_id}"
            query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    user_id BIGINT PRIMARY KEY,
                    channel_name TEXT,
                    channel_id BIGINT,
                    promts TEXT DEFAULT 'Нет',
                    triggers TEXT DEFAULT 'Нет',
                    comments_sent INTEGER DEFAULT 0,
                    monitoring_status BOOLEAN DEFAULT FALSE
                )
            """
            await self.execute_query(query)
            logger.info(f"Created table {table_name} in the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while creating table {table_name}: {error}")

    async def update_comments_sent(self, user_id: int, comments: int) -> None:
        """
        Updates the 'comments_sent' column in the 'subscriptions' table for a specific user.
        """
        try:
            query = "UPDATE subscriptions SET comments_sent = comments_sent + $1 WHERE user_id = $2"
            await self.execute_query(query, comments, user_id)
            logger.info(f"Updated 'comments_sent' for user_id {user_id} in the subscriptions table")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error updating 'comments_sent' for user_id {user_id} in the subscriptions table: {error}")

    async def get_comments_sent(self, user_id: int) -> int:
        """
        Retrieves the value of 'comments_sent' column from the 'subscriptions' table for a specific user.
        """
        try:
            query = "SELECT comments_sent FROM subscriptions WHERE user_id = $1"
            result = await self.pool.fetchval(query, user_id)
            logger.info(f"Retrieved 'comments_sent' for user_id {user_id} from the subscriptions table")
            return result
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving 'comments_sent' for user_id {user_id} from the subscriptions table: {error}")
            return 0

    # ___________________________________________________
    # user_accs_table
    async def create_user_accounts_table(self, user_id: int) -> None:
        """
        Creates a new table in the database with the name "settings_{user_id}" and the specified columns.
        """
        try:
            table_name = f"accounts_{user_id}"
            query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    phone TEXT PRIMARY KEY,
                    comments INTEGER DEFAULT 0,
                    comments_today INTEGER DEFAULT 0,
                    sex TEXT,
                    status TEXT DEFAULT 'Active',
                    in_work BOOLEAN DEFAULT FALSE
                )
            """
            await self.execute_query(query)
            logger.info(f"Created table {table_name} in the database")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while creating table {table_name}: {error}")

    async def get_all_paid_accounts(self) -> Dict[str, List[str]]:
        """
        Retrieves all phone records from tables starting with "accounts_" and returns a dictionary of records.
        """
        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'accounts_%'"
            table_names = await self.fetch_all(query)
            phone_records = {}
            for table_name in table_names:
                query = f"SELECT phone FROM {table_name['table_name']}"
                records = await self.fetch_all(query)
                phone_records[table_name['table_name']] = [record['phone'] for record in records]
            return phone_records
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving phone records from tables", error)
            return {}

    async def get_user_accounts(self, user_id: int) -> List[str]:
        """
        Retrieves all phone numbers from the specified user's accounts table.
        """
        try:
            table_name = f"accounts_{user_id}"
            query = f"SELECT phone FROM {table_name}"
            rows = await self.fetch_all(query)
            phone_numbers = [row[0] for row in rows]
            logger.info(f"Retrieved phone numbers from table {table_name}")
            return phone_numbers
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving phone numbers from table {table_name}: {error}")
            return []

    # ------------------------------------------------------
    # subscriptions table
    async def get_user_ids_by_sub_type(self, sub_type: str) -> List[int]:
        """
        Retrieves a list of user_ids from the subscriptions table with the specified sub_type.
        """
        try:
            query = "SELECT user_id FROM subscriptions WHERE sub_type = $1"
            rows = await self.fetch_all(query, sub_type)
            user_ids = [row[0] for row in rows]
            logger.info(f"Retrieved user_ids with sub_type {sub_type} from the subscriptions table")
            return user_ids
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving user_ids with sub_type {sub_type} from the subscriptions table: {error}")
            return []

    async def update_subscription_type(self, user_id: int, new_sub_type: str) -> None:
        try:
            if new_sub_type == "DEMO":
                query = """
                    UPDATE subscriptions 
                    SET sub_type = $1, 
                        sub_start_date = NULL, 
                        sub_end_date = NULL, 
                        sub_status = FALSE
                    WHERE user_id = $2
                """
                await self.pool.execute(query, new_sub_type, user_id)
            else:
                query = "UPDATE subscriptions SET sub_type = $1 WHERE user_id = $2"
                await self.pool.execute(query, new_sub_type, user_id)
            logger.info(f"Updated subscription type for user_id {user_id} to {new_sub_type}")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error updating subscription type for user_id {user_id}: {error}")

    # ------------------------------------------------------
    # users table
    async def get_user_id_by_username(self, username: str) -> int:
        try:
            query = "SELECT user_id FROM users WHERE user_name = $1"
            row = await self.fetch_row(query, username)
            if row:
                user_id = row[0]
                logger.info(f"Retrieved user_id {user_id} for username {username}")
                return user_id
            else:
                logger.warning(f"No user found with username {username}")
                return None
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving user_id for username {username} from the database: {error}")
            return None

    async def get_username_by_user_id(self, user_id: int) -> str:
        try:
            query = "SELECT user_name FROM users WHERE user_id = $1"
            row = await self.fetch_row(query, user_id)
            if row:
                username = row[0]
                logger.info(f"Retrieved username {username} for user_id {user_id}")
                return username
            else:
                logger.warning(f"No username found for user_id {user_id}")
                return None
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving username for user_id {user_id} from the database: {error}")
            return None

    async def get_user_notifications_status(self, user_id: int) -> str:
        try:
            query = "SELECT notifications FROM users WHERE user_id = $1"
            row = await self.fetch_row(query, user_id)
            if row:
                notifications = row[0]
                return notifications
            else:
                logger.warning(f"User with user_id {user_id} not found in the users table.")
                return ""
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while retrieving user notifications for user_id {user_id}: {error}")
            return ""

    async def toggle_user_notifications(self, user_id: int, notifications: bool) -> None:
        try:
            query = "UPDATE users SET notifications = $1 WHERE user_id = $2"
            await self.execute_query(query, notifications, user_id)
            logger.info(f"Notifications toggled to {notifications} for user_id {user_id}")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while toggling notifications for user_id {user_id}: {error}")

    async def get_users_with_notifications(self) -> List[int]:
        try:
            query = "SELECT user_id FROM users WHERE notifications = TRUE"
            rows = await self.fetch_all(query)
            user_ids = [row[0] for row in rows]
            logger.info("Retrieved user_ids with notifications=True from the database")
            return user_ids
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error retrieving user_ids with notifications=True from the database:", error)
            return []

    # ------------------------------------------------------
    # accounts
    async def move_accounts(self, user_id: int, num_accounts: int) -> None:
        try:
            # Проверить существование таблицы accounts_{user_id}
            query_check_table = f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'accounts_{user_id}')"
            table_exists = await self.execute_query_return(query_check_table)
            if not table_exists[0][0]:
                # Создать таблицу accounts_{user_id}, если она не существует
                table_name = f"accounts_{user_id}"
                query = f"""
                                CREATE TABLE IF NOT EXISTS {table_name} (
                                    phone TEXT PRIMARY KEY,
                                    comments INTEGER DEFAULT 0,
                                    comments_today INTEGER DEFAULT 0,
                                    sex TEXT,
                                    status TEXT DEFAULT 'Active',
                                    in_work BOOLEAN DEFAULT False
                                )
                            """
                await self.execute_query(query)

            # Получить список аккаунтов для перемещения
            query_select = "SELECT phone, sex FROM telegram_accounts LIMIT $1"
            accounts_to_move = await self.execute_query_return(query_select, num_accounts)

            # Переместить аккаунты в таблицу accounts_{user_id}
            query_insert = f"INSERT INTO accounts_{user_id} (phone, sex) VALUES ($1, $2)"
            for account in accounts_to_move:
                phone = account["phone"]
                sex = account["sex"]
                await self.execute_query(query_insert, phone, sex)

            # Удалить перемещенные аккаунты из таблицы telegram_accounts
            query_delete = "DELETE FROM telegram_accounts WHERE phone IN (SELECT phone FROM telegram_accounts LIMIT $1)"
            await self.execute_query(query_delete, num_accounts)

            logger.info(f"Moved {num_accounts} accounts to accounts_{user_id}")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error moving accounts to accounts_{user_id}: {error}")

    async def return_accounts(self, user_id):
        try:
            accounts = await self.fetch_all(f"SELECT phone, sex FROM accounts_{user_id}")
            if accounts:
                for account in accounts:
                    phone = account['phone']
                    sex = account['sex']
                    await self.execute_query("INSERT INTO telegram_accounts (phone, sex) VALUES ($1, $2)", phone, sex)
                await self.execute_query(f"DROP TABLE IF EXISTS accounts_{user_id}")
                logger.info(f"All accounts from accounts_{user_id} table transferred to telegram_accounts table")
            else:
                logger.warning(f"No accounts found in accounts_{user_id} table")
        except Exception as e:
            logger.error(f"Error transferring accounts: {e}")

    # ------------------------------------------------------
    # retrieve all info about accounts from all tables
    async def db_get_all_tg_accounts_with_comments(self, free_accs=True) -> dict:
        """
        Retrieves all Telegram accounts from the database, including tables starting with "accounts_".
        Returns a dictionary where the keys are table names and the values are dictionaries with "phone" and "comments" values.
        """
        try:
            result = {}

            # Retrieve information from the "telegram_accounts" table
            if free_accs:
                query = "SELECT phone, comments, sex FROM telegram_accounts"
                rows = await self.fetch_all(query)
                accounts = [{"phone": row[0], "comments": row[1], "sex": row[2]} for row in rows]
                result["telegram_accounts"] = accounts

            # Retrieve information from tables starting with "accounts_"
            query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'accounts_%'"
            rows = await self.fetch_all(query)
            table_names = [row[0] for row in rows]
            if table_names:
                for table_name in table_names:
                    query = f"SELECT phone, comments, sex FROM {table_name}"
                    rows = await self.fetch_all(query)
                    if not rows:  # Skip the table if it's empty
                        continue
                    accounts = [{"phone": row[0], "comments": row[1], "sex": row[2]} for row in rows]
                    result[table_name] = accounts

            return result
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving Telegram accounts with comments from the database: {error}")
            return {}

    async def increment_comments(self, table_name: str, phone: str) -> None:
        try:
            query = f"UPDATE {table_name} SET comments = comments + 1, comments_today = comments_today + 1 WHERE phone = $1"
            await self.execute_query(query, phone)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error incrementing comments for phone {phone} in table {table_name}: {error}")

    async def get_phones_with_comments_today_less_than(self, table_name: str, max_comments: int) -> List[str]:
        try:
            query = f"SELECT phone FROM {table_name} WHERE comments_today < $1 AND in_work = False"
            rows = await self.execute_query_return(query, max_comments)
            phones = [row[0] for row in rows]
            return phones
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error retrieving phones with comments_today less than {max_comments} from table {table_name}: {error}")
            return []

    async def reset_comments_today(self) -> None:
        try:
            # Reset comments_today in telegram_accounts table
            await self.execute_query("UPDATE telegram_accounts SET comments_today = 0")

            # Get all table names starting with 'accounts_'
            query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'accounts_%'"
            rows = await self.execute_query_return(query)

            if rows:
                table_names = [row[0] for row in rows]

                # Reset comments_today in each accounts_ table
                for table_name in table_names:
                    count_query = f"SELECT COUNT(*) FROM {table_name}"
                    count = await self.execute_query_return(count_query)

                    if count and count[0][0] > 0:
                        await self.execute_query(f"UPDATE {table_name} SET comments_today = 0")

            logger.info("Reset comments_today in telegram_accounts and accounts_ tables")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error resetting comments_today: {error}")

    #sex options
    async def get_sex_by_phone(self, phone: str, uid=False) -> str:
        """
        Retrieves the value from the 'sex' column for the given phone number from the 'telegram_accounts' table.
        Returns the value of 'sex' column as a string.
        """
        try:
            if uid:
                result = await self.execute_query_return(f"SELECT sex FROM accounts_{uid} WHERE phone = $1", phone)
            else:
                result = await self.execute_query_return("SELECT sex FROM telegram_accounts WHERE phone = $1", phone)
            if result:
                sex = result[0][0]
                return sex
            else:
                logger.info('Phone number not found in the table')
                return None
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving sex from the table", error)
            return None

    async def update_user_account_sex(self, user_id: int, phone: str, sex: str) -> None:
        try:
            table_name = f"accounts_{user_id}"
            query = f"""
                UPDATE {table_name}
                SET sex = $1
                WHERE phone = $2
            """
            await self.execute_query(query, sex, phone)
            logger.info(f"Updated sex for account {phone} in table {table_name}")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while updating sex for account {phone} in table {table_name}: {error}")

    async def set_in_work(self, table_name: str, phone: str, stop_work: bool = False) -> None:
        try:
            value = "True" if not stop_work else "False"
            query = f"UPDATE {table_name} SET in_work = {value} WHERE phone = $1"
            await self.execute_query(query, phone)
        except (Exception, asyncpg.PostgresError) as error:
            action = "True" if not stop_work else "False"
            logger.error(f"Error setting in_work={action} for phone {phone} in table {table_name}: {error}")







db = Database()


