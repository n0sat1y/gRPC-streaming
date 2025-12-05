import grpc
from loguru import logger
from src.schemas.websocket import *
from src.schemas.message import ApiGatewayReadEvent
from src.handlers.grpc.message import RpcMessageService
from src.core.kafka import router

class WebsocketHandler:
    def __init__(self, message_service: RpcMessageService):
        self.rpc_message_service = message_service
        self.kafka_router = router
        self._handler = {
            'send_message': self.send_message,
            'edit_message': self.edit_message,
            'delete_message': self.delete_message,
            'mark_as_read': self.mark_as_read,
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
                payload=ErrorPayload(
                    code=e.code().name,
                    details=e.details()
                )
            ).model_dump()


    async def send_message(self, user_id: int, message: SendMessageEvent):
        await self.rpc_message_service.send_message(
            sender_id=user_id,
            chat_id=message.payload.chat_id,
            content=message.payload.content,
            request_id=message.request_id
        )

    async def edit_message(self, user_id: int, message: EditMessageEvent):
        await self.rpc_message_service.update_message(
            sender_id=user_id,
            message_id=message.payload.message_id,
            new_content=message.payload.new_content,
            request_id=message.request_id
        )

    async def delete_message(self, user_id: int, message: DeleteMessageEvent):
        await self.rpc_message_service.delete_message(
            sender_id=user_id,
            message_id=message.payload.message_id,
            request_id=message.request_id
        )

    async def mark_as_read(self, user_id: int, message: ReadMessagesEvent):
        await self.kafka_router.publisher('api_gateway.mark_as_read').publish(
            ApiGatewayReadEvent(
                user_id=user_id,
                chat_id=message.payload.chat_id,
                last_read_message_id=message.payload.last_read_message
            )
        )
        print(message)
