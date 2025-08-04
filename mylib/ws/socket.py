from .basesocket import BaseSocket
from .connection import ConnectionMethods
from .event import EventMethods


class Socket(
    BaseSocket, ConnectionMethods, EventMethods,
    
):
    pass