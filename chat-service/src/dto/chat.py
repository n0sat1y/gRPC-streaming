from dataclasses import dataclass

from typing import Optional, List

@dataclass
class Id:
    id: int

@dataclass
class CreateGroupDTO:
    name: str
    members: List[Id]
    avatar: Optional[str] = None

@dataclass
class UpdateGroupDTO:
    id: int
    name: Optional[str] = None
    avatar: Optional[str] = None
