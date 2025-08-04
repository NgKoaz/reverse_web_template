from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..socket import Socket


class BaseListener:
    def __init__(self, id: int):
        self.id = id

    def check_rdata(self, rdata: list):
        raise NotImplementedError
    
    async def handle(self, socket: 'Socket', rdata: list):
        raise NotImplementedError

