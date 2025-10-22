from loguru import logger
from faststream.kafka import KafkaRouter
from pydantic import TypeAdapter

from src.services.connection import manager
from src.schemas.message import *

router = KafkaRouter()

read_message_pub = router.publisher('api_gateway.messages_read')

@router.subscriber(
    'message.event',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def message_event(data: IncomingMessage):
    message: IncomingMessage = TypeAdapter(IncomingMessage).validate_python(data)
    if message.event_type == 'MessageCreated':
        await send_message(data)
    elif message.event_type == 'MessageUpdated':
        await update_message(data)
    elif message.event_type == 'MessageDeleted':
        await delete_message(data)


async def send_message(data: CreatedMessageEvent):
    logger.info(f"Пришло сообщение {data.event_type}")
    data_dict = data.model_dump(mode='json')
    sender_id = data.sender_id
    recievers = [x for x in data.recievers if x != sender_id]
    payload = data_dict['data']


    await manager.broadcast(
        recievers,
        {
        'event_type': 'new_message',
        'payload': payload
    })

    payload.pop('sender')
    await manager.send_personal_message(
        user_id=sender_id,
        data={
            'event_type': 'message_sended',
            'payload': payload,
            'request_id': data.request_id
        }
    )

async def update_message(data: UpdateMessageEvent):
    logger.info(f"Пришло сообщение {data.event_type}")
    data_dict = data.model_dump(mode='json')
    sender_id = data.sender_id
    recievers = [x for x in data.recievers if x != sender_id]
    payload = data_dict['data']

    await manager.broadcast(
        recievers,
        {
        'event_type': 'update_message',
        'payload': payload
    })

    await manager.send_personal_message(
        user_id=sender_id,
        data={
            'event_type': 'message_updated',
            'payload': payload,
            'request_id': data.request_id
        }
    )

async def delete_message(data: DeleteMessageEvent):
    logger.info(f"Пришло сообщение {data.event_type}")
    data_dict = data.model_dump(mode='json')
    sender_id = data.sender_id
    recievers = [x for x in data.recievers if x != sender_id]
    payload = data_dict['data']

    await manager.broadcast(
        recievers,
        {
        'event_type': 'delete_message',
        'payload': payload
    })

    await manager.send_personal_message(
        user_id=sender_id,
        data={
            'event_type': 'message_deleted',
            'payload': payload,
            'request_id': data.request_id
        }
    )
