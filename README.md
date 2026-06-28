# API Template

> Base template để reverse-engineer và simulate lại API của các website/game.  
> Hỗ trợ cả **HTTP REST** (`src/client`) và **WebSocket** (`src/ws`).

---

## Kiến trúc tổng quan

```
src/
├── client/          # HTTP REST API
│   ├── _base.py     # BaseClient — quản lý httpx session
│   ├── client.py    # Client — class cuối bạn dùng
│   ├── requests/    # Định nghĩa từng API endpoint
│   ├── responses/   # Model response (dataclass)
│   ├── schemas/     # Shared schema/dataclass
│   ├── enums/       # Enum giá trị cố định
│   ├── constants/   # URL, header mặc định
│   └── util/        # Helper functions
│
└── ws/              # WebSocket
    ├── _base.py     # BaseSocket — quản lý WS connection
    ├── socket.py    # Socket — class cuối bạn dùng
    ├── _connection.py  # Mixin: start/stop/listen
    ├── _event.py       # Mixin: on_open/on_message/add_listener
    ├── requests/    # Định nghĩa từng WS command gửi đi
    ├── responses/   # Model response (dataclass)
    ├── listeners/   # Lắng nghe event từ server
    ├── constants/   # Opcode, event ID
    └── util/        # Helper functions
```

---

## Luồng hoạt động

### HTTP
```
Client()(Request) → Request.build() → Request.send() → parse() → Response
```

### WebSocket
```
Socket.start() → _listen() → _on_message() → Listener.should_handle() → Listener.handle()
```

---

## Cách thêm 1 HTTP Endpoint mới

**Ví dụ: API đăng nhập trả về token**

### Bước 1 — Tạo Schema (data model)
```python
# src/client/schemas/login.py
from dataclasses import dataclass
from . import BaseSchema

@dataclass
class LoginSchema(BaseSchema):
    token: str
    user_id: int
    expires_in: int
    # BaseSchema.from_dict() tự parse dict → LoginSchema
    # Đổi thư viện parse → chỉ sửa BaseSchema, không đụng Request
```

### Bước 2 — Tạo Request class
```python
# src/client/requests/login.py
from typing import TYPE_CHECKING
from . import Request
from ..schemas.login import LoginSchema

if TYPE_CHECKING:
    from ..client import Client


class LoginReq(Request[LoginSchema]):
    def __init__(self, username: str, password: str):
        super().__init__(method="POST", url="https://api.example.com/login")
        self.username = username
        self.password = password
        self.response_type = LoginSchema  # Request chỉ biết "parse vào class này"

    def build(self, client: 'Client') -> None:
        self.headers = {
            "content-type": "application/json",
            "origin": "https://example.com",
        }
        self.data = {
            "username": self.username,
            "password": self.password,
        }

    # (tuỳ chọn) hook sau khi parse xong
    async def on_response(self, client: 'Client', data: LoginSchema) -> None:
        client.token = data.token  # lưu token vào client
```

### Bước 3 — Dùng
```python
import asyncio
from src.client import Client
from src.client.requests.login import LoginReq

async def main():
    client = Client()
    result = await client(LoginReq("myuser", "mypass"))
    print(result.token)   # IDE gợi ý đúng type: str

asyncio.run(main())
```

---

## Cách thêm 1 WebSocket Command mới

**Ví dụ: Gửi command vào phòng game, nhận kết quả**

### Bước 1 — Tạo Response model
```python
# src/ws/responses/join_room.py
from dataclasses import dataclass, field
from .base import Response

@dataclass
class JoinRoomResponse(Response):
    room_id: int
    players: list[str] = field(default_factory=list)
```

### Bước 2 — Tạo Request class
```python
# src/ws/requests/join_room.py
import asyncio
from typing import TYPE_CHECKING
from . import Request
from ..listeners import BaseListener
from ..responses.join_room import JoinRoomResponse

if TYPE_CHECKING:
    from ..socket import Socket


class JoinRoomReq(Request[JoinRoomResponse]):
    RESPONSE_EVENT_ID = 42  # opcode server trả về

    def __init__(self, room_id: int):
        super().__init__()
        self.room_id = room_id
        self.response_type = JoinRoomResponse

    def build(self, socket: 'Socket') -> None:
        # Format message gửi lên server (tuỳ protocol của từng website)
        self.msg = [10, {"room": self.room_id, "mid": self._next_msg_id()}]

    def should_handle(self, data: any) -> bool:
        return isinstance(data, list) and data[0] == self.RESPONSE_EVENT_ID

    async def send(self, socket: 'Socket') -> JoinRoomResponse:
        # Đăng ký listener trước khi gửi để không miss response
        listener = Listener(event_id=self.RESPONSE_EVENT_ID, request=self)
        socket.add_listener(listener)

        await socket.ws.send_json(self.msg)

        try:
            raw = await asyncio.wait_for(self.fut, timeout=5.0)
        except TimeoutError:
            socket.remove_listener(listener)
            raise TimeoutError(f"JoinRoomReq timeout, msg={self.msg}")

        return JoinRoomResponse(**raw[1])


class Listener(BaseListener):
    def __init__(self, event_id: int, request: 'JoinRoomReq'):
        super().__init__(event_id=event_id)
        self.request = request

    def should_handle(self, data: any) -> bool:
        return self.request.should_handle(data)
 
    async def handle(self, socket: 'Socket', data: any) -> None:
        socket.remove_listener(self)
        self.request.fut.set_result(data)
```

### Bước 3 — Override `_on_message` trong Socket
```python
# src/ws/socket.py
import json
from ._base import BaseSocket
from ._connection import ConnectionMethods
from ._event import EventMethods


class Socket(BaseSocket, ConnectionMethods, EventMethods):
    async def _on_message(self, message) -> None:
        data = json.loads(message)          # hoặc binary parse nếu binary protocol
        event_id = data[0]                  # tuỳ format của website
        if event_id in self._listeners:
            for listener in self._listeners[event_id]:
                if listener.should_handle(data):
                    await listener.handle(self, data)
```

### Bước 4 — Dùng
```python
import asyncio
from src.ws import Socket
from src.ws.requests.join_room import JoinRoomReq

async def main():
    socket = Socket(url="wss://game.example.com/ws")
    await socket.start()

    result = await socket(JoinRoomReq(room_id=99))
    print(result.room_id, result.players)

    await socket.stop()

asyncio.run(main())
```

---

## Giải thích các pattern nâng cao

### `self: 'Socket'` trong Mixin là gì?
`ConnectionMethods` và `EventMethods` là **Mixin** — chúng không tự đứng độc lập mà được mix vào `Socket`. Dùng `self: 'Socket'` là để IDE biết `self` lúc runtime là `Socket`, từ đó gợi ý đúng attribute như `self._connected`, `self.ws`, v.v.

### `Request[ResType]` Generic là gì?
Giúp type system biết `await client(LoginReq(...))` trả về `LoginResponse`, không phải `Any`. IDE sẽ tự gợi ý field đúng.

### `TYPE_CHECKING` guard là gì?
Tránh **circular import**: `Request` cần import `Client` để type hint, nhưng `Client` cũng import `Request`. Đặt trong `if TYPE_CHECKING:` nghĩa là chỉ import lúc IDE phân tích, không import lúc runtime.

---

## Cài đặt

```bash
pip install -r requirements.txt
pip install -e .   # cài package ở chế độ editable
```

---

## Quy ước đặt tên

| Loại | Quy ước | Ví dụ |
|------|---------|-------|
| File private/internal | prefix `_` | `_base.py`, `_connection.py` |
| Class public | PascalCase | `LoginReq`, `JoinRoomResponse` |
| Constant | UPPER_SNAKE | `BASE_URL`, `DEFAULT_TIMEOUT` |
| Opcode/Event ID | UPPER_SNAKE trong `constants/` | `EVT_JOIN_ROOM = 42` |
| Method override hook | prefix `on_` | `on_response`, `on_message` |
| Method internal | prefix `_` | `_listen`, `_next_msg_id` |
