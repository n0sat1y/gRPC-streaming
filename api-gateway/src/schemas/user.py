from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserData(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)
