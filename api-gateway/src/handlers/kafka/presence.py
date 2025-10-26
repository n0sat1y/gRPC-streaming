from faststream.kafka.fastapi import KafkaRouter

from src.schemas.presence import PresenceEvent
from src.services.connection import manager

router = KafkaRouter()

@router.subscriber(
    'presence.status',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def handle_presence_event(event: PresenceEvent):
    await manager.broadcast(
        recievers=event.recievers,
        data={
            'event_type': 'update_user_status',
            'payload': {
                'user_id': event.user_id,
                'status': event.status
            }
        }
    )


