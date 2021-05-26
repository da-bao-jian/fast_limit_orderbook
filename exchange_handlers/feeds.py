'''
based on cryptofeed https://github.com/bmoscon/cryptofeed/feed.py
'''
from collections import defaultdict
from typing import Union
from .defines import (FUNDING, L2_BOOK, L3_BOOK, OPEN_INTEREST)
class Feed:
    '''
    This is the parent class for individual exchanges
    '''
    def __init__(self, address: Union[dict, str], symbol: str, callbacks, channel: str, token: str= 'USD', subscription: str=None):
        '''
        address: dict or str
            dict for multiple addresses  
            str for a single address 
            address is provided in exchange subclass' argument
        symbol: str
            token subscribed
        callbacks: 
            callback functions that will be invoked for fetching different metrics i.e. Level 2 orderbook, trades, open interest etc. 
        channel: str
            channel subscribed
        '''
        self.subscriptions = defaultdict(set) 
        # multi-channel subscription
        self.subscriptions = {chan: symbol for chan in channel}
        self.callbacks = {
            FUNDING: None,
            L2_BOOK: None,
            L3_BOOK: None,
            OPEN_INTEREST: None
        }

    def start_connection(self):
        '''
        Setup ws connection using self.address
        Create tasks in main event loop
        '''

