from src.routers.kafka import broker
from src.routers.kafka.producer import KafkaPublisher
from src.repositories import UserRepository
from src.services import UserService

producer = KafkaPublisher(broker)
repo = UserRepository()
service = UserService(repo=repo, producer=producer)
