from loguru import logger
from faststream.kafka import KafkaRouter

from src.services.connection import manager

router = KafkaRouter()

@router.subscriber('message.event')
async def send_message(data: dict):
    logger.info(f"Пришло сообщение {data}")
    message_data = data['data']
    recievers = message_data.pop('recievers')
    await manager.broadcast(
        recievers, 
        {
            'event_type': 'new_message',
            'payload': data
        }
    )
