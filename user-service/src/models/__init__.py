from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    created_ad: Mapped[datetime] = mapped_column(server_default=func.now())
