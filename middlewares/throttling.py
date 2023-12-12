import asyncio
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from config import logger
from cachetools import TTLCache

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.processed_messages = set()
        self.pending_actions = []

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        if user_id in self.pending_actions:
            return
        if isinstance(event, Message):
            event_id = event.message_id
            self.pending_actions.append(user_id)
        elif isinstance(event, CallbackQuery):
            event_id = event.message.message_id
            self.pending_actions.append(user_id)
        else:
            return

        # Генерируем уникальный ключ для проверки
        key = f"throttling:{user_id}:{event_id}"
        if key in self.processed_messages:
            # Если сообщение уже было обработано, отменяем обработку
            logger.warning(f"Throttling occurred for user {user_id} and event {event_id}")
            return

        if self.pending_actions.count(user_id) > 1:
            # Если у пользователя уже есть ожидающее действие, возвращаем None
            return

        self.processed_messages.add(key)
        try:
            result = await handler(event, data)
            self.pending_actions.remove(user_id)
            return result
        finally:
            # Удаляем ключ из списка обработанных сообщений
            self.processed_messages.remove(key)
            # Добавляем ожидающее действие для пользователя
            await asyncio.sleep(0.5)
            print('sleep')

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, time_linit: int = 1) -> None:
        self.processed_messages = set()
        self.limit = TTLCache(maxsize=10_000, ttl=time_linit)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        if isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
        else:
            chat_id = event.chat.id

        if chat_id in self.limit:
            return
        else:
            self.limit[chat_id] = None

        return await handler(event, data)
