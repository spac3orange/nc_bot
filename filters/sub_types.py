from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import db


class BasicSub(BaseFilter):
    def __init__(self) -> None:
        self.basic_members = None

    async def __call__(self, message: Message) -> bool:
        self.basic_members = await self.get_basic_members()
        print(self.basic_members)
        print(message.from_user.id in self.basic_members)
        return message.from_user.id in self.basic_members

    async def get_basic_members(self):
        members = await db.get_user_ids_by_sub_type('DEMO')
        return members
