from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..socket import Socket


class BaseListener:
    def __init__(self, event_id: int):
        self.event_id = event_id

    def check_rdata(self, rdata: list) -> bool:
        """Kiểm tra rdata có khớp với listener này không."""
        raise NotImplementedError

    async def handle(self, socket: 'Socket', rdata: list) -> None:
        """Xử lý event khi check_rdata trả về True."""
        raise NotImplementedError
