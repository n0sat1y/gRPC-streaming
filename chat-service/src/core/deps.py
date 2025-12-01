from src.routers.kafka import broker
from src.repositories.chat import ChatRepository
from src.repositories.user import UserRepository
from src.services.chat import ChatService
from src.services.user import UserService
from src.routers.kafka.producer import KafkaPublisher


chat_repo = ChatRepository()
user_repo = UserRepository()
user_service = UserService(user_repo)
kafka_publisher = KafkaPublisher(broker=broker)
chat_service = ChatService(
    producer=kafka_publisher,
    repo=chat_repo,
    user_service=user_service
)
