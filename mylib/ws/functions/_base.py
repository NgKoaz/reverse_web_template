import asyncio

from typing import TYPE_CHECKING, Generic, TypeVar
from ..listeners import BaseListener


if TYPE_CHECKING:
    from ..socket import Socket


ResType = TypeVar("ResType")


class Request(Generic[ResType]):
    __msg_id = 0

    def __init__(self):
        self.msg: list | dict = None
        self.response_type: ResType = None
        self.fut = asyncio.get_running_loop().create_future()

    @classmethod
    def get_next_msg_id(cls):
        cls.__msg_id += 1
        return cls.__msg_id
    
    def build(self, socket: 'Socket'):
        raise NotImplementedError
    
    def check_rdata(self, rdata: list | dict):
        raise NotImplementedError
    
    def on_response(self, socket: 'Socket', rdata: list | dict):
        pass

    # def __gen_listener(self):
    #     self.listener = Listener(id=self.get_second_id(), request=self)
    #     return self.listener

    async def send(self, socket: 'Socket') -> ResType:
        pass
        # socket.add_listener(
        #     self.get_rcmd_id(), 
        #     self.__gen_listener()
        # )

        # await socket.ws.send_json(self.msg)
        # try:
        #     message = await asyncio.wait_for(self.fut, timeout=3)
        # except TimeoutError as e:
        #     print(f"Request data: {self.msg}")
        #     raise e
            
        # self.on_response(socket, message)
        # return message



class Listener(BaseListener):
    def __init__(self, id: str | int, request: Request):
        super().__init__(id=id)
        self.request = request

    def check_rdata(self, rdata: list):
        return self.request.check_rdata(rdata)

    async def handle(self, socket: 'Socket', rdata: list):
        pass
        # socket.remove_listener(self.request.get_rcmd_id(), self)
        # self.request.fut.set_result(rdata)



class Response:
    pass
