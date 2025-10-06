from pydantic import BaseModel

class IdSchema(BaseModel):
    id: int

class ChatResponse(BaseModel):
    id: int
    name: str

class MultipleChatsResponse(BaseModel):
    chats: list[ChatResponse]

class FullChatMember(BaseModel):
    id: int

class ChatData(BaseModel):
    name: str
    members: list[FullChatMember]
    created_at: str


class CreateChatRequest(BaseModel):
    name: str
    members: list[IdSchema]

class AddMembersToChatRequest(BaseModel):
    chat_id: int
    members: list[IdSchema]
