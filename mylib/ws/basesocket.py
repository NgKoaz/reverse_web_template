import asyncio


from aiohttp import ClientSession, ClientWebSocketResponse
from aiohttp_socks import ProxyConnector
from asyncio import Future
from typing import TYPE_CHECKING
from .functions import Request, ResType
from .listeners import BaseListener


if TYPE_CHECKING: 
    from .socket import Socket


class BaseSocket:
    def __init__(self: 'Socket', url: str, *, proxy: str | None = None):
        self.ws: ClientWebSocketResponse = None
        self.url = url

        self._listen_task: asyncio.Task | None = None
        self._ping_task: asyncio.Task | None = None
        
        self._connected = asyncio.Event()
        self._listeners: dict[int, list[BaseListener]] = {}
        
        self._proxy = proxy

    async def __call__(self: 'Socket', req: Request[ResType]) -> ResType:
        req.build(self)
        return await req.send(self)
    
