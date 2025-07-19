from datetime import datetime, timezone

from sqlalchemy import func, select, update

from src.core.logger import logger
from src.db.db_helper import db_helper
from src.db.models import Newsletter, NewsletterStatus, Role, User


async def get_number_of_users() -> int:
    async with db_helper.session_factory() as session:
        result = await session.execute(select(func.count()).select_from(User))
        total = result.scalar()
    return total


async def create_user(telegram_id: int, role: Role) -> User:
    async with db_helper.session_factory() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=telegram_id, role=role)
            session.add(user)
            await session.commit()

    return user


async def make_moderator_from_user(telegram_id: int) -> User:
    async with db_helper.session_factory() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.role = Role.moderator
        else:
            user = User(telegram_id=int(telegram_id), role=Role.moderator)
            session.add(user)
        await session.commit()
    return user


async def get_users() -> list[int]:
    async with db_helper.session_factory() as session:
        result = await session.execute(select(User.telegram_id))
        return result.scalars().all()  # Получаем список всех id


async def get_user_by_id(telegram_id: int) -> User | None:
    async with db_helper.session_factory() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    return user


async def save_planned_message(dt_utc: datetime) -> Newsletter:
    async with db_helper.session_factory() as session:
        newsletter = Newsletter(send_at=dt_utc)
        session.add(newsletter)
        await session.commit()
    return newsletter


async def update_pending_newsletters(newsletter_id: int) -> None:
    async with db_helper.session_factory() as session:
        stmt = (
            update(Newsletter)
            .where(Newsletter.id == newsletter_id)
            .values(status=NewsletterStatus.sent)
        )
        await session.execute(stmt)
        await session.commit()


async def get_pending_newsletters() -> int:
    now = datetime.now(timezone.utc)
    async with db_helper.session_factory() as session:
        stmt = select(func.count()).select_from(Newsletter).where(
            Newsletter.status == NewsletterStatus.pending,
            Newsletter.send_at > now
        )
        result = await session.execute(stmt)
        return result.scalar_one()
