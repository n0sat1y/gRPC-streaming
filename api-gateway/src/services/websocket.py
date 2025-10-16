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
                    message=message.payload
                )
                return None
            elif message.event_type == 'edit_message':
                await self.edit_message(
                    user_id=user_id,
                    message=message.payload
                )
            elif message.event_type == 'delete_message':
                await self.delete_message(
                    user_id=user_id,
                    message=message.payload
                )
        except grpc.RpcError as e:
            return ErrorResponse(
                payload=ErrorPayload(
                    code=e.code().name,
                    details=e.details()
                )
            ).model_dump()


    async def send_message(self, user_id: int, message: SendMessagePayload):
        await self.rpc_message_service.send_message(
            user_id=user_id,
            chat_id=message.chat_id,
            content=message.content,
            tmp_message_id=message.tmp_message_id
        )

    async def edit_message(self, user_id: int, message: EditMessagePayload):
        pass

    async def delete_message(self, user_id: int, message: DeleteMessagePayload):
        pass
