from typing import TYPE_CHECKING
from .listeners import BaseListener

if TYPE_CHECKING:
    from .socket import Socket


class EventMethods:
    async def _on_open(self: 'Socket') -> None:
        self._connected.set()

    async def _on_message(self: 'Socket', message) -> None:
        """Override để xử lý message nhận được từ server."""
        raise NotImplementedError

    def _on_close(self: 'Socket') -> None:
        pass

    def _on_error(self: 'Socket', e: Exception) -> None:
        raise e

    def add_listener(self: 'Socket', nl: BaseListener) -> None:
        """Thêm listener. Nếu cùng object đã tồn tại thì replace, chưa có thì append."""
        listeners = self._listeners.setdefault(nl.event_id, [])
        for i, l in enumerate(listeners):
            if l is nl:
                listeners[i] = nl
                return
        listeners.append(nl)

    def remove_listener(self: 'Socket', target: BaseListener) -> None:
        listeners = self._listeners.get(target.event_id, [])
        self._listeners[target.event_id] = [
            l for l in listeners if l is not target
        ]