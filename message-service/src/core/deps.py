from src.repositories.message import MessageRepository
from src.services.user import UserService
from src.services.chat import ChatService
from src.repositories.user import UserRepository
from src.repositories.chat import ChatRepository
from src.services.message import MessageService
from src.routers.grpc import Message
from src.routers.kafka.producer import KafkaPublisher
from src.routers.kafka import broker

def get_message_repository() -> MessageRepository:
    return MessageRepository()

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_chat_repository() -> ChatRepository:
    return ChatRepository()

def get_kafka_producer() -> KafkaPublisher:
    return KafkaPublisher(broker=broker)

def get_user_service(
        repo: UserRepository = get_user_repository()
    ) -> UserService:
    return UserService(repo=repo)

def get_chat_service(
        repo: ChatRepository = get_chat_repository(),
        user_service: UserService = get_user_service()
    ) -> ChatService:
    return ChatService(repo=repo, user_service=user_service)

def get_message_service(
        repo: MessageRepository = get_message_repository(),
        user_service: UserService = get_user_service(),
        chat_service: ChatService = get_chat_service(),
        kafka_producer: KafkaPublisher = get_kafka_producer()
    ) -> MessageService:
    return MessageService(
        repo=repo,
        user_service=user_service,
        chat_service=chat_service,
        kafka_producer=kafka_producer
    )

def get_grpc_message_service(
        chat_service: ChatService = get_chat_service(),
        message_service: MessageService = get_message_service()
    ) -> Message:
    return Message(
        chat_service=chat_service,
        message_service=message_service
    )
