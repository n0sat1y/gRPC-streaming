from enum import IntEnum, auto

class ChatTypeEnum(IntEnum):
    GROUP = auto()           
    PRIVATE = auto()        
    CHANNEL = auto()         
    SAVED_MESSAGES = auto()   
