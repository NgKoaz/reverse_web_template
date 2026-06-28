from dataclasses import dataclass
from dacite import from_dict, Config
from typing import TypeVar, Type


T = TypeVar("T", bound="BaseSchema")


@dataclass
class BaseSchema:
    """
    Base class cho tất cả response/data models.

    Subclass này để định nghĩa schema cho từng endpoint:

        @dataclass
        class UserSchema(BaseSchema):
            id: int
            name: str
            email: str

    Tự động parse từ dict:

        user = UserSchema.from_dict({"id": 1, "name": "Alice", "email": "a@b.com"})

    Đổi thư viện parse → chỉ sửa `from_dict()` ở đây, không đụng vào Request.
    """

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        return from_dict(cls, data, config=Config(strict=False))
