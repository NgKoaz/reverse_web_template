from typing import TYPE_CHECKING

from .listeners import BaseListener

if TYPE_CHECKING:
    from .socket import Socket




class EventMethods:
    async def _on_open(self: 'Socket'):
        self._connected.set()

    async def _on_message(self: 'Socket', message):
        pass
        # data = json.loads(message)
        # if data[0] in self._listeners:
        #     ls = self._listeners[data[0]]
        #     for l in ls:
        #         if l.check_rdata(data):
        #             await l.handle(self, data)

    def _on_close(self: 'Socket'):
        pass

    def _on_error(self: 'Socket', e):
        raise e
    
    def add_listener(self: 'Socket', nl: BaseListener):
        self._listeners.setdefault(nl.id, [])
        
        listeners = self._listeners[nl.id]
        for i, l in enumerate(listeners):
            if l.id == nl.id:
                listeners[i] = nl 
                break
        else:
            listeners.append(nl)

    def remove_listener(self: 'Socket', target: BaseListener):
        listeners = self._listeners.get(target.id, [])
        self._listeners[target.id] = [
            l for l in listeners
            if not l == target
        ]
        