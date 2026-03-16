from fastapi import Depends
from faststream.kafka.fastapi import KafkaRouter

from src.core.kafka import router
from src.dependencies import get_redis_publisher
from src.infrastructure.redis_publishers.notifier import RedisNotifier
from src.schemas.events.presence import PresenceEvent


@router.subscriber(
    "presence.status", group_id="api-gateway_presence", auto_offset_reset="earliest"
)
async def handle_presence_event(
    event: PresenceEvent, publisher: RedisNotifier = Depends(get_redis_publisher)
):
    status = event.status
    user_id = event.user_id
    print(event)
    await publisher.broadcast(
        recievers=event.recievers,
        data={
            "event_type": "update_user_status",
            "payload": {"user_id": user_id, "status": status},
        },
    )
