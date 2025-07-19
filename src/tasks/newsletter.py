import asyncio
from typing import Optional

from aiogram import Bot

from src.core.celery_app import celery_app
from src.core.config import settings
from src.core.logger import logger
from src.db import crud
from src.schemas.newsletter import NewsletterMessage


@celery_app.task(name="src.tasks.send_message_task")
def send_message_task(user_ids: list[int], message_data: dict, newsletter_id: int):
    logger.info("Начинаю выполнение отложенной задачи")

    try:
        message = NewsletterMessage(**message_data)
    except Exception as e:
        logger.error(f"Неверный формат message_data: {e}")
        return

    bot = Bot(token=settings.tg_token)

    async def _send():
        for user_id in user_ids:
            try:
                if message.text:
                    await bot.send_message(
                        user_id,
                        message.text,
                        parse_mode=message.parse_mode,
                        reply_markup=(
                            _build_keyboard(message.keyboard)
                            if message.keyboard
                            else None
                        ),
                    )
                # тут возможно расширить отправку для фото и видео, пока только текст
                await asyncio.sleep(0.1)  # Чтобы не упереться в 429
            except Exception as e:
                logger.warning(f"Ошибка при отправке {user_id}: {e}")
        # Закрываем соединение и обновляем статус рассылаемого сообщения
        await bot.session.close()
        await crud.update_pending_newsletters(newsletter_id)

    # Запустим для простоты асинхронный цикл вручную
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(_send())


def _build_keyboard(keyboard: list) -> Optional["InlineKeyboardMarkup"]:
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=btn.text, url=str(btn.url)) for btn in row]
            for row in keyboard
        ]
    )
