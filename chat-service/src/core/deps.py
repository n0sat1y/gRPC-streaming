from src.routers.kafka import broker
from src.repositories.chat import ChatRepository
from src.repositories.user import UserRepository
from src.services.chat import ChatService
from src.services.user import UserService


chat_repo = ChatRepository()
user_repo = UserRepository()
user_service = UserService(user_repo)
chat_service = ChatService(
    broker=broker,
    repo=chat_repo,
    user_service=user_service
)
