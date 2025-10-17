import grpc
from src.schemas.websocket import *
from src.handlers.grpc.message import RpcMessageService

class WebsocketHandler:
    def __init__(self):
        self.rpc_message_service = RpcMessageService()

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
