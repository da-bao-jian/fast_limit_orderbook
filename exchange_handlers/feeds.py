'''
based on cryptofeed https://github.com/bmoscon/cryptofeed/feed.py
'''
from .symbols_parser import Symbols
import asyncio
from collections import defaultdict
import logging
from typing import Union, Dict
from .defines import (FUNDING, L2_BOOK, L3_BOOK, OPEN_INTEREST)
from .connection import WSAsyncConn, HTTPAsyncConn, HTTPSync
from .connection_handler import ConnectionHandler
from .standards import feed_to_exchange, is_authenticated_channel
LOG = logging.getLogger('feedhandler')

class UnsupportedSymbol(Exception):
    pass


class Feed:
    id='NotImplemented'
    http_sync = HTTPSync()
    '''
    This is the parent class for individual exchanges
    '''
    def __init__(self, address: Union[dict, str], callbacks: dict, token: str= 'USD', subscription: str=None, retries: int = 10, symbols=None, channels=None ):
        '''
        address: dict or str
            dict for multiple addresses  
            str for a single address 
            address is provided in exchange subclass' argument
        symbol: str
            token subscribed
        callbacks: dict 
            callback functions that will be invoked for fetching different metrics i.e. Level 2 orderbook, trades, open interest etc.
            Preprocessed in the Feed class __init__ method and mostly used in exchange subclasses
        channels: str
            channels subscribed
        '''
        self.subscriptions = defaultdict(set) 
        self.address = address
        self.connections = []
        # ping_pong is used as websockets.connect argument in WSAsyncConn class
        self.ping_pong = {'ping_interval': 10, 'ping_timeout': None, 'max_size': 2**23, 'max_queue': None}
        self.retries = retries

        symbols_cache = Symbols
        if not symbols_cache.populated(self.id):
            self.symbol_mapping()

        self.normalized_symbol_mapping, self.exchange_info = symbols_cache.get(self.id)
        self.exchange_symbol_mapping = {v: k for v, k in self.normalized_symbol_mapping.items()}

        if symbols and channels:
            if any(is_authenticated_channel(chan) for chan in channels):
                if not self.key_id or not self.key_secret:
                    raise ValueError("Authenticated channel subscribed to, but no auth keys provided")
            # if we dont have a subscription dict, we'll use symbols+channels and build one
            self.normalized_symbols = symbols
            # convert the exchange specific symbol to uniform symbols
            symbols = [self.std_symbol_to_exchange_symbol(symbol) for symbol in symbols]
            channels = list(set([feed_to_exchange(self.id, chan) for chan in channels]))
            self.subscription = {chan: symbols for chan in channels}

        self.callbacks = {
            FUNDING: None,
            L2_BOOK: None,
            L3_BOOK: None,
            OPEN_INTEREST: None
        }
        self.http_conn = HTTPAsyncConn(self.id) 
        for cb_type, cb_func in callbacks.items():
            self.callbacks[cb_type] = cb_func
        for key, callback in self.callbacks.items():
            if not isinstance(callback, list):
                self.callbacks[key] = [callback]

    @classmethod
    def symbol_mapping(cls, symbol_separator='-', refresh=False) -> Dict:
        '''
        Map all of the token symbol and exchange info into a Symbols class Dict object to store subscribed channel/symbols in uniform format
        '''
        if Symbols.populated(cls.id) and not refresh:
            return Symbols.get(cls.id)[0]
        try:
            LOG.debug("%s: reading symbol information from %s", cls.id, cls.symbol_endpoint)
            if isinstance(cls.symbol_endpoint, list):
                # some exchanges have multiple endpoints, like Deribit, so they are stored in lists 
                data = []
                for ep in cls.symbol_endpoint:
                    data.append(cls.http_sync.read(ep, json=True, uuid=cls.id))
            else:
                data = cls.http_sync.read(cls.symbol_endpoint, json=True, uuid=cls.id)
            syms, info = cls._parse_symbol_data(data, symbol_separator)
            Symbols.set(cls.id, syms, info)
            return syms
        except Exception as e:
            LOG.error("%s: Failed to parse symbol information: %s", cls.id, str(e), exc_info=True)
            raise

    def exchange_symbol_to_std_symbol(self, symbol: str):
        try:
            return self.exchange_symbol_mapping[symbol]
        except KeyError:
            raise UnsupportedSymbol(f'{symbol} is not supported on {self.id}')

    def std_symbol_to_exchange_symbol(self, symbol: str) -> str:
        try:
            return self.normalized_symbol_mapping[symbol]
        except KeyError:
            raise UnsupportedSymbol(f'{symbol} is not supported on {self.id}')


    def start_connection(self, loop):
        '''
        loop: Asyncio object
            Setup ws connection using self.address
            Create tasks in main event loop
        '''
        if isinstance(self.address, str):
            ws_array = [(WSAsyncConn(self.address, self.id, **self.ping_pong), self.subscribe, self.message_handler)]
        else:
            ws_array = []
            for _, addr in self.address.items():
                ws_array.append((WSAsyncConn(self.address, self.id, **self.ping_pong), self.subscribe, self.message_handler))
        for conn, sub, handler in ws_array:
            self.connections.append(ConnectionHandler(conn, sub, handler, self.retries))
            # start a new task for the latest added connection handler
            self.connections[-1].start(loop)

    async def message_handler(self, msg: str, conn: WSAsyncConn, timestamp: float):
        raise NotImplementedError

    async def subscribe(self, conn: WSAsyncConn, **kwargs):
        """
        kwargs will not be passed from anywhere, if you need to supply extra data to
        your subscribe, bind the data to the method with a partial
        """
        raise NotImplementedError

    async def shutdown(self):
        LOG.info("%s: feed shutdown starting ...", self.id)

        # await self.http_conn.close()
        for conn in self.connections:
            await conn.conn.close()
        LOG.info("%s: feed shutdown completed", self.id)

    def stop(self):
        for conn in self.connections:
            conn.running = False