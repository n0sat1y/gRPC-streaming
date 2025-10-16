from loguru import logger
from faststream.kafka import KafkaRouter

from src.services.connection import manager
from src.schemas.message import CreatedMessageEvent

router = KafkaRouter()

@router.subscriber(
    'message.event',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def send_message(data: CreatedMessageEvent):
    logger.info(f"Пришло сообщение {data.event_type}")
    data_dict = data.model_dump(mode='json')
    sender_id = data.data.sender.id
    recievers = [x for x in data_dict.pop('recievers') if x != sender_id]

    payload_for_recievers = data_dict['data']
    payload_for_sender = payload_for_recievers.copy()

    payload_for_recievers.pop('tmp_message_id')
    await manager.broadcast(
        recievers,
        {
        'event_type': 'new_message',
        'payload': payload_for_recievers
    })
    payload_for_sender.pop('sender')
    await manager.send_personal_message(
        user_id=sender_id,
        data={
            'event_type': 'message_sended',
            'payload': payload_for_sender
        }
    )
