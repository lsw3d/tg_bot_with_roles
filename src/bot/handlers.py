import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.bot.filters import RoleFilter
from src.core.logger import logger
from src.db import crud
from src.db.models import Role
from src.schemas.newsletter import NewsletterMessage
from src.tasks.newsletter import send_message_task

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, role: Role):
    logger.info(
        "%s с telegram_id=%r активировал бота", role.value, message.from_user.id
    )
    await crud.create_user(telegram_id=message.from_user.id, role=role.value)
    await message.answer(
        f"Привет! Спасибо за подписку, ожидай рассылки!\nТвоя роль: {role.value}"
    )


@router.message(Command("get_number_of_users"), RoleFilter([Role.admin]))
async def get_number_of_users(message: Message):
    logger.info("Админ узнал количество юзеров")
    total = await crud.get_number_of_users()
    await message.answer(f"Количество пользователей: {total}")


@router.message(Command("set_moder_by_id"), RoleFilter([Role.admin]))
async def set_moder_by_id(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Укажи ID пользователя: /set_moder_to_id <telegram_id>")
        return

    try:
        telegram_id = int(command.args.strip())
    except ValueError:
        await message.answer("ID должен быть целым числом!")
        return

    logger.info("Назначаем администратора: %s", telegram_id)
    await crud.make_moderator_from_user(telegram_id=telegram_id)
    await message.answer(f"Пользователь с ID {telegram_id} теперь модератор.")
    logger.info("Получил user_id %s", telegram_id)


@router.message(Command("get_planned_newsletter"), RoleFilter([Role.admin]))
async def get_planned_newsletter(message: Message):
    logger.info("Админ узнает количество запланированных писем")
    nums_newsletters = await crud.get_pending_newsletters()
    await message.answer(
        f"Количество запланированных рассылаемых сообщений: {nums_newsletters}"
    )


class NewsletterStates(StatesGroup):
    waiting_for_schedule_time = State()


@router.message(Command("send_newsletter"), RoleFilter([Role.moderator, Role.admin]))
async def send_newsletter(message: Message, command: CommandObject, state: FSMContext):
    logger.info("Сохраняю письмо")
    text = (command.args or "").strip()
    if not text:
        await message.answer("Ты не указал текст рассылки. Попробуй снова.")
        return

    msg = NewsletterMessage(text=text)
    await state.update_data(msg=msg)
    await state.set_state(NewsletterStates.waiting_for_schedule_time)
    await message.answer(
        "Введите время отправки в формате <b>ДД.ММ.ГГГГ ЧЧ:ММ</b>", parse_mode="HTML"
    )


@router.message(NewsletterStates.waiting_for_schedule_time)
async def process_schedule_time(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer(
            "Неверный формат времени. Попробуй снова: <b>ДД.ММ.ГГГГ ЧЧ:ММ</b>",
            parse_mode="HTML",
        )
        return
    # Эту логику лучше вынести в services, однако из-за простоты оставим пока здесь
    dt = dt.replace(tzinfo=ZoneInfo("Europe/Moscow"))
    dt_utc = dt.astimezone(ZoneInfo("UTC"))
    logger.info("Распарсил время отправки отложенной задачи: %s", dt)

    data = await state.get_data()
    user_ids = await crud.get_users()
    newsletter = await crud.save_planned_message(dt_utc=dt_utc)

    logger.info("Отправляю сообщение в celery")
    await asyncio.to_thread(
        send_message_task.apply_async,
        args=(user_ids, data.get("msg").dict(), newsletter.id),
        eta=dt_utc,
    )
    await message.answer(
        f"Сообщение будет отправлено {dt.strftime('%d.%m.%Y %H:%M')} по МСК"
    )
    await state.clear()
