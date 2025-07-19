import inflect
from sqlalchemy.orm import DeclarativeBase, declared_attr

p = inflect.engine()


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls):
        return p.plural(cls.__name__.lower())
