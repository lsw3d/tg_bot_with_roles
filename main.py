import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import router
from src.bot.middlewares import RoleMiddleware
from src.core.config import settings
from src.core.lifespan import router as lifespan_router
from src.db.db_helper import db_helper


async def main():
    storage = MemoryStorage()
    bot = Bot(token=settings.tg_token)
    dp = Dispatcher(storage=storage)

    dp.message.outer_middleware(RoleMiddleware(db_helper))

    dp.include_router(lifespan_router)
    dp.include_router(router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
