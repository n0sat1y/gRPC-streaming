from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.postgres import Base

class ChatMemberReplica(Base):
    __tablename__ = 'chat_member_replica'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int]
    user_id: Mapped[int]

    __table_args__ = (
        UniqueConstraint('chat_id', 'user_id'),
    )
