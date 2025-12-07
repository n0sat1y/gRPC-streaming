from typing import Literal, Union
from pydantic import BaseModel, model_validator

class IdSchema(BaseModel):
    id: int

class UserEvent(BaseModel):
    event_type: str
    data: Union[IdSchema]

