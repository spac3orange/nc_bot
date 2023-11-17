from aiogram.filters import BaseFilter
from aiogram.types import Message
from database import db
from data.logger import logger


class KnownUser(BaseFilter):

    async def get_known_users(self):
        return await db.db_get_users()

    async def __call__(self, message: Message) -> bool:
        known_users = await self.get_known_users()
        known_users_list = [x[0] for x in known_users]

        valid_user = message.from_user.id in known_users_list
        logger.warning(f'{message.from_user.username} connected\n'
                       f'ID: {message.from_user.id}\n'
                       f'User {message.from_user.username} is KnownUser: {valid_user}')
        return valid_user


