from typing import Literal, Optional, Union

from pydantic import BaseModel


class PayloadBase(BaseModel):
    pass


class EventBase(BaseModel):
    event_type: str
    payload: PayloadBase
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    details: str


class ErrorResponse(BaseModel):
    event_type: Literal["error"] = "error"
    payload: ErrorPayload


class SendMessagePayload(PayloadBase):
    chat_id: int
    content: str
    reply_to: Optional[str] = None


class DeleteMessagePayload(PayloadBase):
    message_id: str


class EditMessagePayload(DeleteMessagePayload):
    new_content: str


class ReadMessagesPayload(PayloadBase):
    chat_id: int
    last_read_message: str


class AddReactionPayload(PayloadBase):
    message_id: str
    reaction: str


class RemoveReactionPayload(PayloadBase):
    message_id: str
    reaction: str


class ForwardMessagesPayload(PayloadBase):
    chat_id: int
    messages: list[str]
    content: Optional[str] = None


class SendMessageEvent(EventBase):
    event_type: Literal["send_message"]
    payload: SendMessagePayload


class DeleteMessageEvent(EventBase):
    event_type: Literal["delete_message"]
    payload: DeleteMessagePayload


class EditMessageEvent(EventBase):
    event_type: Literal["edit_message"]
    payload: EditMessagePayload


class ReadMessagesEvent(EventBase):
    event_type: Literal["mark_as_read"]
    payload: ReadMessagesPayload


class AddReactionEvent(EventBase):
    event_type: Literal["add_reaction"]
    payload: AddReactionPayload


class RemoveReactionEvent(EventBase):
    event_type: Literal["remove_reaction"]
    payload: RemoveReactionPayload


class ForwardMessagesEvent(EventBase):
    event_type: Literal["forward_messages"]
    payload: ForwardMessagesPayload


IncomingMessage = Union[
    SendMessageEvent,
    DeleteMessageEvent,
    EditMessageEvent,
    ReadMessagesEvent,
    AddReactionEvent,
    RemoveReactionEvent,
    ForwardMessagesEvent,
]
