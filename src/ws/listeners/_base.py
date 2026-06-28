from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..socket import Socket


class BaseListener:
    def __init__(self, event_id: int):
        self.event_id = event_id

    def should_handle(self, data: any) -> bool:
        """Kiểm tra data có khớp với listener này không."""
        raise NotImplementedError

    async def handle(self, socket: 'Socket', data: any) -> None:
        """Xử lý event khi should_handle trả về True."""
        raise NotImplementedError
