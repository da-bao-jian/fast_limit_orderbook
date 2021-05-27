'''
based on cryptofeed https://github.com/bmoscon/cryptofeed/feed.py
'''
from collections import defaultdict
from typing import Union
from .defines import (FUNDING, L2_BOOK, L3_BOOK, OPEN_INTEREST)
from .connection import WSAsyncConn
from .connection_handler import ConnectionHandler
class Feed:
    '''
    This is the parent class for individual exchanges
    '''
    def __init__(self, address: Union[dict, str], symbol: str, callbacks: dict, channel: str, token: str= 'USD', subscription: str=None, retries: int = 10):
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
        channel: str
            channel subscribed
        '''
        self.subscriptions = defaultdict(set) 
        # multi-channel subscription for symbols
        self.subscriptions = {chan: symbol for chan in channel}
        # ping_pong is used as websockets.connect argument in WSAsyncConn class
        self.connections = []
        self.ping_pong = {'ping_interval': 10, 'ping_timeout': None, 'max_size': 2**23, 'max_queue': None}
        self.retries = retries
        self.callbacks = {
            FUNDING: None,
            L2_BOOK: None,
            L3_BOOK: None,
            OPEN_INTEREST: None
        }
        for cb_type, cb_func in callbacks.items():
            self.callbacks[cb_type] = cb_func
        for key, callback in self.callbacks.items():
            if not isinstance(callback, list):
                self.callbacks[key] = [callback]

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
            self.connection.append(ConnectionHandler(conn, sub, handler, self.retries))

