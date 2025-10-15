from loguru import logger
from faststream.kafka import KafkaRouter

from src.services.connection import manager

router = KafkaRouter()

@router.subscriber(
    'message.event',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def send_message(data: dict):
    logger.info(f"Пришло сообщение {data}")
    recievers = data.pop('recievers')
    await manager.broadcast(
        recievers, 
        {
            'event_type': 'new_message',
            'payload': data
        }
    )
