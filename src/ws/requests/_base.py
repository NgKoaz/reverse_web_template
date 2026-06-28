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
        self.response_type: type[ResType] | None = self._get_response_type()
        self.fut: asyncio.Future = asyncio.get_running_loop().create_future()

    @classmethod
    def _get_response_type(cls) -> type[ResType] | None:
        for base in getattr(cls, "__orig_bases__", []):
            if hasattr(base, "__args__") and base.__args__:
                return base.__args__[0]
        return None

    @classmethod
    def _next_msg_id(cls) -> int:
        cls._msg_id += 1
        return cls._msg_id

    def build(self, socket: 'Socket') -> None:
        raise NotImplementedError

    def should_handle(self, rdata: list | dict) -> bool:
        raise NotImplementedError

    def parse(self, data: dict) -> ResType:
        """
        Parse raw dict → typed schema.
        Logic parse nằm trong schema.from_dict(), không nằm ở đây.
        """
        if self.response_type is None:
            return data

        # Optional: Handle packet if response_type has from_packet method
        if hasattr(self.response_type, 'from_dict'):
            return self.response_type.from_dict(data)

        return data

    def on_response(self, socket: 'Socket', data: ResType) -> None:
        """Hook sau khi parse xong. Override để xử lý side-effect."""
        pass

    async def send(self, socket: 'Socket') -> ResType:
        # TODO: Implement send
        raise NotImplementedError


class OnceListener(BaseListener):
    def __init__(self, event_id: int, request: Request):
        super().__init__(event_id=event_id)
        self.request = request

    def should_handle(self, rdata: list) -> bool:
        return self.request.should_handle(rdata)

    async def handle(self, socket: 'Socket', rdata: list) -> None:
        socket.remove_listener(self)
        self.request.fut.set_result(rdata)

