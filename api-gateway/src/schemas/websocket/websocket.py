from typing import Literal, Optional, Union

from pydantic import BaseModel


class ErrorPayload(BaseModel):
    code: str
    details: str


class ErrorResponse(BaseModel):
    event_type: Literal["error"] = "error"
    payload: ErrorPayload


class SendMessagePayload(BaseModel):
    chat_id: int
    content: str
    reply_to: Optional[str] = None


class DeleteMessagePayload(BaseModel):
    message_id: str


class EditMessagePayload(DeleteMessagePayload):
    new_content: str


class ReadMessagesPayload(BaseModel):
    chat_id: int
    last_read_message: str


class AddReactionPayload(BaseModel):
    message_id: str
    reaction: str


class RemoveReactionPayload(BaseModel):
    message_id: str
    reaction: str


class SendMessageEvent(BaseModel):
    event_type: Literal["send_message"]
    payload: SendMessagePayload
    request_id: str


class DeleteMessageEvent(BaseModel):
    event_type: Literal["delete_message"]
    payload: DeleteMessagePayload
    request_id: str


class EditMessageEvent(BaseModel):
    event_type: Literal["edit_message"]
    payload: EditMessagePayload
    request_id: str


class ReadMessagesEvent(BaseModel):
    event_type: Literal["mark_as_read"]
    payload: ReadMessagesPayload


class AddReactionEvent(BaseModel):
    event_type: Literal["add_reaction"]
    payload: AddReactionPayload


class RemoveReactionEvent(BaseModel):
    event_type: Literal["remove_reaction"]
    payload: RemoveReactionPayload


IncomingMessage = Union[
    SendMessageEvent,
    DeleteMessageEvent,
    EditMessageEvent,
    ReadMessagesEvent,
    AddReactionEvent,
    RemoveReactionEvent,
]
