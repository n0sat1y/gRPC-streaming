import grpc
from src.schemas.websocket import *
from src.schemas.message import ApiGatewayReadEvent
from src.handlers.grpc.message import RpcMessageService
from src.handlers.kafka.message import router

class WebsocketHandler:
    def __init__(self):
        self.rpc_message_service = RpcMessageService()
        self.kafka_router = router

    async def handle_incoming_message(self, user_id: int, message: IncomingMessage):
        try:
            if message.event_type == 'send_message':
                await self.send_message(
                    user_id=user_id,
                    message=message
                )
                return None
            elif message.event_type == 'edit_message':
                await self.edit_message(
                    user_id=user_id,
                    message=message
                )
            elif message.event_type == 'delete_message':
                await self.delete_message(
                    user_id=user_id,
                    message=message
                )
            elif message.event_type == 'mark_as_read':
                await self.read_messages(
                    user_id=user_id,
                    message=message
                )
                print('new_message_read')
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

    async def read_messages(self, user_id: int, message: ReadMessagesEvent):
        await self.kafka_router.publisher('api_gateway.mark_as_read').publish(
            ApiGatewayReadEvent(
                user_id=user_id,
                chat_id=message.payload.chat_id,
                last_read_message_id=message.payload.last_read_message
            )
        )
        print(message)
