import grpc
from google.protobuf.json_format import MessageToDict

from protos import chat_pb2, chat_pb2_grpc
from src.services import ChatService


class Chat(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.service = ChatService()

    async def GetUserChats(self, request, context):
        chats = await self.service.get_user_chats(request.user_id, context)
        return chat_pb2.MultipleChatsResponse(
            chats=[chat_pb2.ChatResponse(id=model.id, name=model.name) for model in chats]
        )
    
    async def CreateChat(self, request, context):
        data = MessageToDict(request, preserving_proto_field_name=True)
        chat = await self.service.create(data, context)
        return chat_pb2.ChatResponse(id=chat.id, name=chat.name)
    
    async def GetChatData(self, request, context):
        chat = await self.service.get(request.chat_id, context)
        created_at_str = chat.created_at.isoformat()
        return chat_pb2.ChatData(
            name=chat.name,
            members=[chat_pb2.FullChatMember(id=member.user_id, username=member.username) for member in chat.members],
            created_at=created_at_str,
        )

    async def AddMembersToChat(self, request, context):
        data_dict = MessageToDict(request, preserving_proto_field_name=True)
        chat_id = data_dict.pop('chat_id')
        members = data_dict.pop('members')
        chat = await self.service.add_members(chat_id, members, context)
        return chat_pb2.ChatResponse(id=chat.id, name=chat.name)
