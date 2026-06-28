from ._base import BaseSocket
from ._connection import ConnectionMethods
from ._event import EventMethods


class Socket(
    BaseSocket, ConnectionMethods, EventMethods,
):
    pass