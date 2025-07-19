from aiogram import Bot, Dispatcher, Router

from src.core.config import settings
from src.core.logger import logger
from src.db import crud
from src.db.db_helper import db_helper
from src.db.models import Role

router = Router()


@router.startup()
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    logger.info("Запуск бота! Создаю таблички...")
    await db_helper.create_all_tables()

    # Хардкодим админа через конфиг для простоты
    await crud.create_user(settings.admin_tg_id, role=Role.admin)


@router.shutdown()
async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    logger.info("Бот выключается! Удаляю таблички...")
    await db_helper.drop_all_tables()
