'''
Copied from cryptofeed https://github.com/bmoscon/cryptofeed/connection.py
'''
import logging
from typing import Union
import websockets
import aiohttp
from contextlib import asynccontextmanager
LOG = logging.getLogger('feedhandler')


class Connection:
    raw_data_callback = None

    async def read(self) -> bytes:
        raise NotImplementedError

    async def write(self, msg: str):
        raise NotImplementedError

class AsyncConnection(Connection):
    conn_count: int = 0

    def __init__(self, conn_id: str):
        """
        conn_id: str
            the unique identifier for the connection
        """
        AsyncConnection.conn_count += 1
        self.id: str = conn_id
        self.received: int = 0
        self.sent: int = 0
        self.last_message = None
        self.conn: Union[websockets.WebSocketClientProtocol, aiohttp.ClientSession] = None

    @property
    def uuid(self):
        return self.id

    @asynccontextmanager
    async def connect(self):
        await self._open()
        try:
            yield self
        finally:
            await self.close()

    async def _open(self):
        raise NotImplementedError

    @property
    def is_open(self) -> bool:
        raise NotImplementedError

    async def close(self):
        if self.is_open:
            conn = self.conn
            self.conn = None
            await conn.close()
            LOG.info('%s: closed connection %r', self.id, conn.__class__.__name__)