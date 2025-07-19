import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String

from src.db.db_helper import Base


class Role(enum.Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class User(Base):
    telegram_id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(Role), default=Role.user, nullable=False)


class NewsletterStatus(enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Newsletter(Base):
    id = Column(Integer, primary_key=True)
    send_at = Column(DateTime, nullable=False)
    status = Column(Enum(NewsletterStatus), default="pending")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
