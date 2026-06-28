import httpx

from typing import TYPE_CHECKING
from .requests import Request, ResType


if TYPE_CHECKING:
    from .client import Client


class BaseClient:
    def __init__(
        self,
        proxy: str | None = None,
    ):
        self.conn = httpx.AsyncClient(follow_redirects=True, proxy=proxy)

    async def __call__(self: 'Client', req: 'Request[ResType]') -> ResType:
        req.build(self)
        return await req.send(self)
