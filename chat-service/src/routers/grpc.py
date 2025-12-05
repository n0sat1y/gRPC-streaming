from google.protobuf.json_format import MessageToDict
from loguru import logger
from faststream.kafka import KafkaBroker

from protos import chat_pb2, chat_pb2_grpc
from src.services.chat import ChatService
from src.routers.kafka import broker
from src.decorators import handle_exceptions
from src.enums.enums import ChatTypeEnum
from src.dto.chat import *


class Chat(chat_pb2_grpc.ChatServicer):
    def __init__(
        self,
        service: ChatService
    ):
        self.service = service

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
                interlocutor = next(
                    (x for x in model.members if x.user_id != current_user_id),
                    None
                )
                chat_response.title = 'Deleted Account'
                if interlocutor:
                    chat_response.interlocutor_id = interlocutor.user_id
                    if interlocutor.user:
                        chat_response.title = interlocutor.user.username
                        if avatar := interlocutor.user.avatar:
                            chat_response.avatar = avatar
                    else:
                        chat_response.title = 'Unknown User'

            elif model.chat_type == ChatTypeEnum.SAVED_MESSAGES:
                chat_response.type = chat_pb2.SAVED_MESSAGES
                chat_response.interlocutor_id = current_user_id
                chat_response.title = 'Saved Messages'
            
            elif model.chat_type == ChatTypeEnum.GROUP:
                chat_response.type = chat_pb2.GROUP
                chat_response.title = model.name
                if model.avatar:
                    chat_response.avatar = model.avatar
            print(chat_response)
            response_chats.append(chat_response)
        return chat_pb2.MultipleChats(chats=response_chats)
    
    @handle_exceptions
    async def CreateGroupChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        logger.info("Поступил запрос на создание группового чата")
        members_dto = [Id(id=x.id) for x in request.members]
        data_dto = CreateGroupDTO(
            name=request.name,
            members=members_dto,
            avatar=request.avatar
        )
        chat = await self.service.create_group(data_dto)
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def GetOrCreatePrivateChat(self, request, context):
        logger.info(f"Поступил запрос на получение приватного чата")
        chat = await self.service.get_or_create_private(
            request.current_user_id,
            request.target_user_id
        )
        response = chat_pb2.ChatId(id=chat.id)
        return response
    
    @handle_exceptions
    async def GetChatData(self, request, context):
        user_id, chat_id = request.user_id, request.chat_id
        logger.info(f"Поступил запрос на получение данных чата {request.chat_id}")
        chat = await self.service.get(chat_id)

        response = chat_pb2.ChatData()
        response.id = chat.id
        
        if chat.chat_type == ChatTypeEnum.PRIVATE:
            response.type = chat_pb2.PRIVATE
            interlocutor = next(
                (x for x in chat.members if x.user_id != user_id),
                None
            )
            response.title = 'Deleted Account'
            if interlocutor:
                response.interlocutor_id = interlocutor.user_id
                if interlocutor.user:
                    response.title = interlocutor.user.username
                    avatar = interlocutor.user.avatar
                    if avatar:
                        response.avatar = avatar
                else:
                    response.title = 'Unknown User'

        elif chat.chat_type == ChatTypeEnum.SAVED_MESSAGES:
            response.type = chat_pb2.SAVED_MESSAGES
            response.interlocutor_id = user_id
            response.title = 'Saved Messages'

        elif chat.chat_type == ChatTypeEnum.GROUP:
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
        data_dto = UpdateGroupDTO(**data)
        logger.info(f"Поступил запрос на обновление чата {data_dto.id}")
        chat = await self.service.update(data_dto)
        return chat_pb2.ChatId(id=chat.id)
    
    @handle_exceptions
    async def AddMembersToChat(self, request, context):
        chat_id = request.id
        members = [member.id for member in request.members]
        logger.info(f"Поступил запрос на добавление участников в чат {chat_id}")
        chat = await self.service.add_members(chat_id, members)
        return chat_pb2.ChatId(id=chat.id)

    @handle_exceptions
    async def DeleteUserChat(self, request, context):
        logger.info(f"Поступил запрос на удаление пользователя {request.user_id} из чата {request.chat_id}")
        response = await self.service.delete_user_from_chat(request.user_id, request.chat_id)
        return chat_pb2.DeleteResponse(status=response)
    
    @handle_exceptions
    async def DeleteChat(self, request, context):
        logger.info(f"Поступил запрос на удаление чата {request.id}")
        response = await self.service.delete(request.id)
        return chat_pb2.DeleteResponse(status=response)

    @handle_exceptions
    async def GetLastReadMessage(self, request, context):
        chat_id = request.chat_id
        user_id = request.user_id
        logger.info(f"Получен запрос на просмотр последнего прочитанного сообщения чата {chat_id} ползователем {user_id}")
        chat_member = await self.service.get_chat_member(chat_id, user_id)
        return chat_pb2.MessageId(message_id=chat_member.last_read_message_id)
