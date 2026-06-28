from typing import Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


ResType = TypeVar("ResType")


class Request(Generic[ResType]):
    def __init__(self, method: str, url: str):
        self.method = method
        self.headers: dict[str, str] | None = None
        self.url = url
        self.params: dict | None = None
        self.data: dict | None = None
        self.response_type: type[ResType] | None = None

    def build(self, client: 'Client') -> None:
        raise NotImplementedError

    def parse(self, data: dict) -> ResType:
        """
        Parse raw dict → typed schema.
        Logic parse nằm trong schema.from_dict(), không nằm ở đây.
        """
        if self.response_type is None:
            return data
        if hasattr(self.response_type, 'from_dict'):
            return self.response_type.from_dict(data)
        return data

    @staticmethod
    def _get_headers(overrides: dict[str, str] | None = None) -> dict[str, str]:
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
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }
        if overrides:
            headers = default_headers.copy()
            headers.update(overrides)
            return headers
        return default_headers

    async def on_response(self, client: 'Client', data: ResType) -> None:
        """Hook sau khi nhận response. Override để lưu token, cookie, v.v."""
        pass

    async def send(self, client: 'Client') -> ResType:
        req = client.conn.build_request(
            method=self.method,
            url=self.url,
            headers=self._get_headers(self.headers),
            params=self.params,
            data=self.data,
        )
        res = await client.conn.send(req)
        data = self.parse(res.json())
        await self.on_response(client, data)
        return data
