from typing import TYPE_CHECKING
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

import asyncio


if TYPE_CHECKING:
    from .socket import Socket


class ConnectionMethods:
    async def start(self: 'Socket') -> None:
        """Connect và bắt đầu lắng nghe WebSocket."""
        self._listen_task = asyncio.create_task(self._listen())
        await self._connected.wait()

    async def stop(self: 'Socket') -> None:
        """Dừng kết nối WebSocket."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

    async def _listen(self: 'Socket') -> None:
        try:
            connector = ProxyConnector.from_url(self._proxy) if self._proxy else None
            async with ClientSession(connector=connector) as session:
                async with session.ws_connect(self.url) as ws:
                    self.ws = ws
                    await self._on_open()
                    async for message in self.ws:
                        await self._on_message(message.data)
        except Exception as e:
            self._on_error(e)
        finally:
            self._on_close()
