import grpc
from loguru import logger

from src.core.kafka import router
from src.infrastructure.grpc_clients.message import RpcMessageService
from src.schemas.events.message import ApiGatewayReadEvent
from src.schemas.websocket.websocket import *


class WebsocketHandler:
    def __init__(self, message_service: RpcMessageService):
        self.rpc_message_service = message_service
        self.kafka_router = router
        self._handler = {
            "send_message": self.send_message,
            "edit_message": self.edit_message,
            "delete_message": self.delete_message,
            "mark_as_read": self.mark_as_read,
            "add_reaction": self.add_reaction,
            "remove_reaction": self.remove_reaction,
        }

    async def handle_incoming_message(self, user_id: int, message: IncomingMessage):
        try:
            event = self._handler.get(message.event_type, None)
            if not event:
                logger.warning(f"Неизвестный тип события: {message.event_type}")
                return
            await event(user_id, message)
        except grpc.RpcError as e:
            return ErrorResponse(
                payload=ErrorPayload(code=e.code().name, details=e.details())
            ).model_dump()

    async def send_message(self, user_id: int, message: SendMessageEvent):
        await self.rpc_message_service.send_message(
            sender_id=user_id,
            chat_id=message.payload.chat_id,
            content=message.payload.content,
            request_id=message.request_id,
            reply_to=message.payload.reply_to,
        )

    async def edit_message(self, user_id: int, message: EditMessageEvent):
        await self.rpc_message_service.update_message(
            sender_id=user_id,
            message_id=message.payload.message_id,
            new_content=message.payload.new_content,
            request_id=message.request_id,
        )

    async def delete_message(self, user_id: int, message: DeleteMessageEvent):
        await self.rpc_message_service.delete_message(
            sender_id=user_id,
            message_id=message.payload.message_id,
            request_id=message.request_id,
        )

    async def mark_as_read(self, user_id: int, message: ReadMessagesEvent):
        await self.kafka_router.publisher("api_gateway.mark_as_read").publish(
            ApiGatewayReadEvent(
                user_id=user_id,
                chat_id=message.payload.chat_id,
                last_read_message_id=message.payload.last_read_message,
            )
        )
        print(message)

    async def add_reaction(self, user_id: int, message: AddReactionEvent):
        await self.rpc_message_service.add_reaction(
            author=user_id,
            message_id=message.payload.message_id,
            reaction=message.payload.reaction,
        )

    async def remove_reaction(self, user_id: int, message: RemoveReactionEvent):
        print(message)
        await self.rpc_message_service.remove_reaction(
            author=user_id,
            message_id=message.payload.message_id,
            reaction=message.payload.reaction,
        )
