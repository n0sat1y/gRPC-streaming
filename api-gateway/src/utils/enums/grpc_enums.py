from enum import Enum


class DirectionEnum(Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    UNSPECIFIED = "UNSPECIFIED"


direction_enum_mapper = {
    DirectionEnum.UNSPECIFIED: 0,
    DirectionEnum.BEFORE: 1,
    DirectionEnum.AFTER: 2,
}
