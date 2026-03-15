from faststream.kafka.fastapi import KafkaRouter

from src.core.kafka import router
from src.dependencies import get_non_dependend_connection_manager
from src.schemas.events.presence import PresenceEvent

connection_manager = get_non_dependend_connection_manager()


@router.subscriber(
    "presence.status", group_id="api-gateway_presence", auto_offset_reset="earliest"
)
async def handle_presence_event(event: PresenceEvent):
    status = event.status
    user_id = event.user_id
    print(event)
    await connection_manager.broadcast(
        recievers=event.recievers,
        data={
            "event_type": "update_user_status",
            "payload": {"user_id": user_id, "status": status},
        },
    )
