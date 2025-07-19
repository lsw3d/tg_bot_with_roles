from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.core.logger import logger
from src.db import crud
from src.db.models import Role


class RoleMiddleware(BaseMiddleware):
    def __init__(self, db_helper):
        super().__init__()
        self.db_helper = db_helper

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        telegram_id = None
        if isinstance(event, Message):
            telegram_id = event.from_user.id
        # TODO: Добавить обработку других событий

        logger.info("Проверяю роль пользователя id=%r", telegram_id)
        if telegram_id:
            user = await crud.get_user_by_id(telegram_id=telegram_id)
            if user:
                data["role"] = (
                    Role(user.role) if isinstance(user.role, str) else user.role
                )
            else:
                data["role"] = Role.user
        else:
            data["role"] = Role.user

        return await handler(event, data)
