'''
based on cryptofeed https://github.com/bmoscon/cryptofeed/feed.py
'''
from .symbols_parser import Symbols
from .util import book_delta
import asyncio
from collections import defaultdict
import logging
from typing import Union, Dict
from .defines import FUNDING, L2_BOOK, L3_BOOK, OPEN_INTEREST, BID, ASK, BOOK_DELTA
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
    def __init__(self, address: Union[dict, str], callbacks: dict, token: str= 'USD', cross_check = False,  subscription: str=None, snapshot_interval = False, max_depth = None, retries: int = 10, symbols=None, channels=None ):
        '''
        address: dict or str
            dict for multiple addresses  
            str for a single address 
            address is provided in exchange subclass' argument
        symbol: str
            token subscribed
        max_depth: int
            Maximum number of levels per side to return in book updates
        callbacks: dict 
            callback functions that will be invoked for fetching different metrics i.e. Level 2 orderbook, trades, open interest etc.
            Preprocessed in the Feed class __init__ method and mostly used in exchange subclasses
        snapshot_interval: bool/int
            Number of updates between snapshots. Only applicable when book delta is not enabled.
            Updates between snapshots are not delivered to the client
        channels: str
            channels subscribed
        cross_check: bool
            Toggle a check for a crossed book. Should not be needed on exchanges that support
            checksums or provide message sequence numbers.
        '''
        self.subscriptions = defaultdict(set) 
        self.address = address
        self.do_deltas = False
        self.snapshot_interval = snapshot_interval
        self.max_depth = max_depth
        self.cross_check = cross_check
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
    
    async def book_callback(self, book: dict, book_type: str, symbol: str, forced: bool, delta: dict, timestamp: float, receipt_timestamp: float):
        """
        ** for the purpose of BST implementation, it doesn't matter what to put into the Feed() args, it should only needs to handle the
        update in the exchange specific class, for reference check out the FTX class' book method's update portion



        Three cases we need to handle here

        1.  Book deltas are enabled (application of max depth here is trivial)
        1a. Book deltas are enabled, max depth is not, and exchange does not support deltas. Rare
        2.  Book deltas not enabled, but max depth is enabled
        3.  Neither deltas nor max depth enabled
        4.  Book deltas disabled and snapshot intervals enabled (with/without max depth)

        2 and 3 can be combined into a single block as long as application of depth modification
        happens first

        For 1, need to handle separate cases where a full book is returned vs a delta
        """
        # if you put BOOK_DELTA in the callbacks arg in the Feed(), self.do_deltas will be true here and it will do the following
        if self.do_deltas:
            # if self.updates < self.book_update_interval, it will it will only call self.callback(BOOK_DELTA...) 
            if not forced and self.updates[symbol] < self.book_update_interval:
                if self.max_depth:
                    delta, book = await self.apply_depth(book, True, symbol)
                    if not (delta[BID] or delta[ASK]):
                        return
                elif not delta:
                    # this will only happen in cases where an exchange does not support deltas and max depth is not enabled.
                    # this is an uncommon situation. Exchanges that do not support deltas will need
                    # to populate self.previous internally to avoid the unncesessary book copy on all other exchanges
                    delta = book_delta(self.previous_book[symbol], book, book_type=book_type)
                    if not (delta[BID] or delta[ASK]):
                        return
                # add update by one
                self.updates[symbol] += 1
                if self.cross_check:
                    self.check_bid_ask_overlapping(book, symbol)
                # call BOOK_DELTA callback
                await self.callback(BOOK_DELTA, feed=self.id, symbol=symbol, delta=delta, timestamp=timestamp, receipt_timestamp=receipt_timestamp)
                # if update times is smaller than book_update_interval, this function stops, otherwise, it goes to the bottom and fetch the whole book again
                if self.updates[symbol] != self.book_update_interval:
                    return
            elif forced and self.max_depth:
                # We want to send a full book update but need to apply max depth first
                _, book = await self.apply_depth(book, False, symbol)
        elif self.max_depth:
            if not self.snapshot_interval or (self.snapshot_interval and self.updates[symbol] >= self.snapshot_interval):
                changed, book = await self.apply_depth(book, False, symbol)
                if not changed:
                    return
        # case 4 - increment skipped update, and exit
        if self.snapshot_interval and self.updates[symbol] < self.snapshot_interval:
            self.updates[symbol] += 1
            return

        if self.cross_check:
            self.check_bid_ask_overlapping(book, symbol)
        if book_type == L2_BOOK:
            await self.callback(L2_BOOK, feed=self.id, symbol=symbol, book=book, timestamp=timestamp, receipt_timestamp=receipt_timestamp)
            # await self.callback(BOOK_DELTA, feed=self.id, symbol=symbol, delta=delta, timestamp=timestamp, receipt_timestamp=receipt_timestamp)
        else:
            await self.callback(L3_BOOK, feed=self.id, symbol=symbol, book=book, timestamp=timestamp, receipt_timestamp=receipt_timestamp)
        self.updates[symbol] = 0

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

    async def callback(self, data_type, **kwargs):
        for cb in self.callbacks[data_type]:
            await cb(**kwargs)

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