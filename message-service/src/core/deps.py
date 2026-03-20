from src.repositories.chat import ChatRepository
from src.repositories.message import MessageRepository
from src.repositories.read_progress import ReadProgressRepository
from src.repositories.user import UserRepository
from src.routers.grpc import Message
from src.routers.kafka import broker
from src.routers.kafka.producer import KafkaPublisher
from src.services.chat import ChatService
from src.services.message import MessageService
from src.services.policy import AccessPolicy
from src.services.user import UserService


def get_message_repository() -> MessageRepository:
    return MessageRepository()


def get_read_progress_repository() -> ReadProgressRepository:
    return ReadProgressRepository()


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_chat_repository() -> ChatRepository:
    return ChatRepository()


def get_access_policy() -> AccessPolicy:
    return AccessPolicy()


def get_kafka_producer() -> KafkaPublisher:
    return KafkaPublisher(broker=broker)


def get_user_service(repo: UserRepository = get_user_repository()) -> UserService:
    return UserService(repo=repo)


def get_chat_service(
    repo: ChatRepository = get_chat_repository(),
    user_service: UserService = get_user_service(),
) -> ChatService:
    return ChatService(repo=repo, user_service=user_service)


def get_message_service(
    repo: MessageRepository = get_message_repository(),
    read_progress_repo: ReadProgressRepository = get_read_progress_repository(),
    user_service: UserService = get_user_service(),
    chat_service: ChatService = get_chat_service(),
    kafka_producer: KafkaPublisher = get_kafka_producer(),
    access_policy: AccessPolicy = get_access_policy(),
) -> MessageService:
    return MessageService(
        repo=repo,
        read_pregress_repo=read_progress_repo,
        user_service=user_service,
        chat_service=chat_service,
        kafka_producer=kafka_producer,
        access_policy=access_policy,
    )


def get_grpc_message_service(
    chat_service: ChatService = get_chat_service(),
    message_service: MessageService = get_message_service(),
) -> Message:
    return Message(chat_service=chat_service, message_service=message_service)
