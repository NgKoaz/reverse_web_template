from dataclasses import is_dataclass
from dacite import from_dict, Config
from typing import Generic, TypeVar
from ..client import Client


ResType = TypeVar('ResType')


class Request(Generic[ResType]):
    def __init__(self, method: str, url: str):
        self.method = method
        self.headers = None
        self.url = url
        self.params = None
        self.data = None
        self.response_type: ResType = None

    def build(self, client: 'Client'):
        raise NotImplementedError
    
    def parse(self, data) -> ResType:
        try:
            if self.response_type and is_dataclass(self.response_type):
                return from_dict(self.response_type, data, config=Config(strict=False))
            return data
        except Exception as e:
            print(data)
            raise e

    @staticmethod
    def __get_headers(overrides: dict[str, str]):
        default_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "vi-VN,vi;q=0.9",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }
        if overrides:
            headers = default_headers.copy()
            headers.update(overrides)
            return headers
        return default_headers
    
    async def on_response(self, client: 'Client', res: ResType): 
        return

    async def send(self, client: 'Client') -> ResType:
        req = client.conn.build_request(
            method=self.method,
            url=self.url,
            headers=self.__get_headers(self.headers),
            params=self.params,
            data=self.data
        )

        res = await client.conn.send(req)

        data = self.parse(res.json())
        await self.on_response(client, data)
        return data
