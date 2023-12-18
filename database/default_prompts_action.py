import asyncpg
from data import logger
from . db_action import db
from typing import List


async def add_default_prompt(prompt_text: str) -> None:
    """
    Adds a default prompt to the "default_prompts" table.
    """
    try:
        await db.execute_query("INSERT INTO default_prompts (prompt_text) VALUES ($1)", prompt_text)
        logger.info('default prompt added to the table')
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while adding default prompt to the table", error)


async def get_all_default_prompts() -> List[str]:
    """
    Retrieves all default prompts from the "default_prompts" table.
    Returns a list of prompt texts.
    """
    try:
        result = await db.execute_query_return("SELECT prompt_text FROM default_prompts")
        prompts = [row[0] for row in result]
        return prompts
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while retrieving default prompts from the table", error)
        return []


async def delete_default_prompt(prompt_index: int) -> bool:
    """
    Deletes a default prompt from the "default_prompts" table based on the index.
    Returns True if the prompt is deleted, False if the prompt is not found.
    """
    try:
        result = await db.execute_query_return("SELECT prompt_text FROM default_prompts OFFSET $1 LIMIT 1", prompt_index-1)
        if result:
            prompt_text = result[0][0]
            await db.execute_query_return("DELETE FROM default_prompts WHERE prompt_text = $1", prompt_text)
            logger.info('default prompt deleted from the table')
            return True
        else:
            logger.info('default prompt not found')
            return False
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while deleting default prompt from the table", error)
        return False
