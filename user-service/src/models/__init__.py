from datetime import datetime
from sqlalchemy import func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(index=True)
    password: Mapped[bytes]
    avatar: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        UniqueConstraint('username', 'is_active'),
    )
