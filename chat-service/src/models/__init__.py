from datetime import datetime
from sqlalchemy import DateTime, UniqueConstraint, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

class ChatModel(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    avatar: Mapped[str] = mapped_column(nullable=True)
    last_message: Mapped[str] = mapped_column(nullable=True)
    last_message_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    members: Mapped[list["ChatMemberModel"]] = relationship(
		"ChatMemberModel", 
		back_populates="chat"
	)

class ChatMemberModel(Base):
    __tablename__ = 'chat_members'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users_replication.id'))
    last_read_message_id: Mapped[str] = mapped_column(nullable=True)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    chat: Mapped[list["ChatModel"]] = relationship(
		"ChatModel", 
		back_populates="members"
	)

    user: Mapped["UserReplicaModel"] = relationship(
        "UserReplicaModel",
        primaryjoin="ChatMemberModel.user_id == UserReplicaModel.id",
        lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint('chat_id', 'user_id', name='_chat_user_uc'),
    )

class UserReplicaModel(Base):
    __tablename__ = 'users_replication'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
