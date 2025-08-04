from typing import TYPE_CHECKING
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

import asyncio


if TYPE_CHECKING:
    from .socket import Socket




class ConnectionMethods:
    async def start(self: 'Socket'):
        self._listen_task = asyncio.create_task(self._listen())
        await self._connected.wait()
    
    async def stop(self: 'Socket'):
        self._listen_task.cancel()
        try:
            await self._listen_task
        except asyncio.CancelledError:
            pass

    async def _listen(self: 'Socket'):
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

    # async def _ping(self: 'Socket', game_zome: str):
    #     return await self(PingReq(game_zome))

    # def start_ping(self: 'Socket', sleep_time: float=5):
    #     async def wrapper():
    #         while True:
    #             await self._ping(self.game_zone)
    #             await asyncio.sleep(sleep_time)
    #     self._ping_task = asyncio.create_task(wrapper())
    
    # def stop_ping(self: 'Socket'):
    #     if self._ping_task:
    #         self._ping_task.cancel()
    #         self._ping_task = None
