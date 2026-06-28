from dataclasses import dataclass
from dacite import from_dict, Config
from typing import TypeVar, Type


T = TypeVar("T", bound="BaseSchema")


@dataclass
class BaseSchema:
    """
    Base class cho tất cả WS response/data models.

    Ví dụ:

        @dataclass
        class JoinRoomSchema(BaseSchema):
            room_id: int
            players: list[str]

    Parse từ raw data:

        schema = JoinRoomSchema.from_dict(raw_data[1])
    """

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        return from_dict(cls, data, config=Config(strict=False))

