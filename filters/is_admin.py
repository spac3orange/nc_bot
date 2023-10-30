from aiogram.filters import BaseFilter
from data import config_aiogram
from aiogram.types import Message


class IsAdmin(BaseFilter):
    """
        A filter to check if the user is an admin based on their user ID.
        Attributes:
            admin_ids (List[int]): A list of admin user IDs.
        Methods:
            __init__(self, admin_ids: List[int]) -> None: Initializes the IsAdmin filter.
            __call__(self, message: Message) -> bool: Checks if the user is an admin based on their user ID.
        Example usage:
            is_admin_filter = IsAdmin(admin_ids=[123, 456])
            # ...
            if await is_admin_filter(message):
                # User is an admin
            else:
                # User is not an admin
        """
    def __init__(self, admin_id: list[int]) -> None:
        self.admin_ids = config_aiogram.admin_id

    async def __call__(self, message: Message) -> bool:
        return str(message.from_user.id) in self.admin_ids
