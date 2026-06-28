import asyncio

from typing import TYPE_CHECKING, Generic, TypeVar
from ..listeners import BaseListener


if TYPE_CHECKING:
    from ..socket import Socket


ResType = TypeVar("ResType")


class Request(Generic[ResType]):
    _msg_id: int = 0

    def __init__(self):
        self.msg: list | dict | None = None
        self.response_type: type[ResType] | None = None
        self.fut: asyncio.Future = asyncio.get_running_loop().create_future()

    @classmethod
    def _next_msg_id(cls) -> int:
        cls._msg_id += 1
        return cls._msg_id

    def build(self, socket: 'Socket') -> None:
        raise NotImplementedError

    def check_rdata(self, rdata: list | dict) -> bool:
        raise NotImplementedError

    def parse(self, data: dict) -> ResType:
        """
        Parse raw dict → typed schema.
        Logic parse nằm trong schema.from_dict(), không nằm ở đây.
        """
        if self.response_type is None:
            return data
        if hasattr(self.response_type, 'from_dict'):
            return self.response_type.from_dict(data)
        return data

    def on_response(self, socket: 'Socket', data: ResType) -> None:
        """Hook sau khi parse xong. Override để xử lý side-effect."""
        pass

    async def send(self, socket: 'Socket') -> ResType:
        raise NotImplementedError


class Listener(BaseListener):
    def __init__(self, event_id: int, request: Request):
        super().__init__(event_id=event_id)
        self.request = request

    def check_rdata(self, rdata: list) -> bool:
        return self.request.check_rdata(rdata)

    async def handle(self, socket: 'Socket', rdata: list) -> None:
        # Tự remove trước để không fire lại nếu cùng event xảy ra lần 2
        socket.remove_listener(self)
        self.request.fut.set_result(rdata)

