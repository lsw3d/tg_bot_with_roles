from typing import Sequence

from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.core.logger import logger
from src.db.models import Role


class RoleFilter(BaseFilter):
    def __init__(self, roles: Sequence) -> None:
        self.roles = roles

    async def __call__(self, message: Message, role: Role | None = None) -> bool:
        logger.info("Фильтрую роль: %s", role)
        return role in self.roles
