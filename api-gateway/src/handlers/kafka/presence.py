from faststream.kafka.fastapi import KafkaRouter

from src.schemas.presence import PresenceEvent
from src.services.connection import manager
from src.dependencies import get_presence_service

router = KafkaRouter()

@router.subscriber(
    'presence.status',
    group_id='api-gateway',
    auto_offset_reset='earliest'
)
async def handle_presence_event(event: PresenceEvent):
    status = event.status
    user_id = event.user_id

    await manager.broadcast(
        recievers=event.recievers,
        data={
            'event_type': 'update_user_status',
            'payload': {
                'user_id': user_id,
                'status': status
            }
        }
    )
    if event.status == 'offline':
        await manager.kill(user_id, presence_service=None, set_offline=False)


