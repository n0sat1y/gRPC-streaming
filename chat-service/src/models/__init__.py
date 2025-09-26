from datetime import datetime
from sqlalchemy import UniqueConstraint, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

class ChatModel(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    members: Mapped[list["ChatMemberModel"]] = relationship(
		"ChatMemberModel", 
		back_populates="chat"
	)

class ChatMemberModel(Base):
    __tablename__ = 'chat_members'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'))
    user_id: Mapped[int]
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    chat: Mapped[list["ChatModel"]] = relationship(
		"ChatModel", 
		back_populates="members"
	)

    __table_args__ = (
        UniqueConstraint('chat_id', 'user_id', name='_chat_user_uc'),
    )
