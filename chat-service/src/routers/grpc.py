from google.protobuf.json_format import MessageToDict
from loguru import logger

from protos import chat_pb2, chat_pb2_grpc
from src.services.chat import ChatService
from src.routers.kafka import broker
from src.decorators import handle_exceptions
from src.enums.enums import ChatTypeEnum


class Chat(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.service = ChatService()
        self.broker = broker

    @handle_exceptions
    async def GetUserChats(self, request, context):
        current_user_id = request.id
        logger.info(f"Поступил запрос на получение чатов пользователя {current_user_id}")
        
        chats = await self.service.get_user_chats(current_user_id)
        response_chats = []

        for model in chats:
            chat_response = chat_pb2.ChatResponse()
            chat_response.id = model.id
            
            if model.last_message:
                chat_response.last_message = model.last_message
            if model.last_message_at:
                chat_response.last_message_at.FromDatetime(model.last_message_at)

            if model.chat_type == ChatTypeEnum.PRIVATE:
                chat_response.type = chat_pb2.PRIVATE
                chat_response.interlocutor_id = current_user_id
                chat_response.title = "Private Chat"

            else:
                chat_response.type = chat_pb2.GROUP
                chat_response.title = model.name
                if model.avatar:
                    chat_response.avatar = model.avatar
            response_chats.append(chat_response)
        return chat_pb2.MultipleChats(chats=response_chats)
    
    @handle_exceptions
    async def CreateGroupChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        logger.info("Поступил запрос на создание группового чата")
        chat = await self.service.create_group(data, self.broker)
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def GetOrCreatePrivateChat(self, request, context):
        logger.info("Поступил запрос на получение или создания личного чата")
        chat = await self.service.create_group(
            request.current_user_id, 
            request.target_user_id, 
            self.broker
        )
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def GetChatData(self, request, context):
        logger.info(f"Поступил запрос на получение данных чата {request.id}")
        chat = await self.service.get(request.id)

        response = chat_pb2.ChatData()
        response.id = chat.id
        
        if chat.chat_type == ChatTypeEnum.PRIVATE:
            response.type = chat_pb2.PRIVATE
            response.title = "Private Chat"

        else:
            response.type = chat_pb2.GROUP
            response.title = chat.name
            if chat.avatar:
                response.avatar = chat.avatar

        if chat.last_message:
            response.last_message = chat.last_message
        if chat.last_message_at:
            response.last_message_at.FromDatetime(chat.last_message_at)
            
        response.members.extend([chat_pb2.UserId(id=member.user_id) for member in chat.members])
        response.created_at.FromDatetime(chat.created_at)
        print(response)
        return response
        
    @handle_exceptions
    async def UpdateChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        chat_id = data.pop('id')
        logger.info(f"Поступил запрос на обновление чата {chat_id}")
        chat = await self.service.update(chat_id, data)
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def AddMembersToChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        print(data)
        chat_id = data.pop('id')
        members = data.pop('members')
        logger.info(f"Поступил запрос на добавление участников в чат {chat_id}")
        chat = await self.service.add_members(chat_id, members, self.broker)
        return chat_pb2.ChatId(id=chat.id)

    @handle_exceptions
    async def DeleteUserChat(self, request, context):
        logger.info(f"Поступил запрос на удаление пользователя {request.user_id} из чата {request.chat_id}")
        response = await self.service.delete_user_from_chat(request.user_id, request.chat_id, self.broker)
        return chat_pb2.DeleteResponse(status=response)
    
    @handle_exceptions
    async def DeleteChat(self, request, context):
        logger.info(f"Поступил запрос на удаление чата {request.id}")
        response = await self.service.delete(request.id, self.broker)
        return chat_pb2.DeleteResponse(status=response)

    @handle_exceptions
    async def GetLastReadMessage(self, request, context):
        chat_id = request.chat_id
        user_id = request.user_id
        logger.info(f"Получен запрос на просмотр последнего прочитанного сообщения чата {chat_id} ползователем {user_id}")
        chat_member = await self.service.get_chat_member(chat_id, user_id)
        return chat_pb2.MessageId(message_id=chat_member.last_read_message_id)
