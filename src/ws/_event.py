from typing import TYPE_CHECKING
from .listeners import BaseListener

if TYPE_CHECKING:
    from .socket import Socket


class EventMethods:
    async def _on_open(self: 'Socket') -> None:
        self._connected.set()

    async def _on_message(self: 'Socket', message) -> None:
        """
        Base routing: parse message → dispatch đến các listener phù hợp.
        Không override method này. Override `_parse_message` để handle format
        của từng website (JSON, binary, v.v.)
        """
        event_id, data = self._parse_message(message)
        await self._dispatch(event_id, data)

    def _parse_message(self: 'Socket', message) -> tuple[int, any]:
        """
        Override method này trong subclass để parse raw message → (event_id, data).
        Mỗi website có format khác nhau, ví dụ:
            JSON:   data = json.loads(message); return data[0], data[1]
            Binary: return struct.unpack('>H', message[:2])[0], message[2:]
        """
        raise NotImplementedError

    async def _dispatch(self: 'Socket', event_id: int, data) -> None:
        """Tìm và gọi tất cả listener khớp với event_id."""
        for listener in list(self._listeners.get(event_id, [])):
            if listener.check_rdata(data):
                await listener.handle(self, data)

    def _on_close(self: 'Socket') -> None:
        pass

    def _on_error(self: 'Socket', e: Exception) -> None:
        raise e

    def add_listener(self: 'Socket', nl: BaseListener) -> None:
        """Thêm listener. Bỏ qua nếu đã tồn tại (tránh duplicate)."""
        listeners = self._listeners.setdefault(nl.event_id, [])
        if nl not in listeners:
            listeners.append(nl)

    def remove_listener(self: 'Socket', target: BaseListener) -> None:
        listeners = self._listeners.get(target.event_id, [])
        self._listeners[target.event_id] = [
            l for l in listeners if l is not target
        ]