import httpx


from typing import TYPE_CHECKING
from .functions import Request, ResType


if TYPE_CHECKING:
    from .client import Client




class BaseClient:
    def __init__(
        self: 'Client',
        proxy: str = None
    ):
        self.conn = httpx.AsyncClient(follow_redirects=True, proxy=proxy)

    async def __call__(self, req: Request[ResType]):
        req.build(self)
        raw = await req.send(self)
        return raw
    
