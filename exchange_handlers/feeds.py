'''
based on cryptofeed https://github.com/bmoscon/cryptofeed
'''
from collections import defaultdict
from typing import Union
from .defines import (FUNDING, L2_BOOK, L3_BOOK, OPEN_INTEREST)
class Feed:
    '''
    This is the parent class for individual exchanges
    '''
    def __init__(self, address: Union[dict, str], symbol: str = None, callbacks = None, channel: str=None, subscription: str=None):
        '''
        address: dict or str
            dict for multiple addresses - wss and http 
            str for a single address 
        symbol: str
            token subscribed
        callbacks: 
            callback functions that will be invoked for fetching different metrics i.e. Level 2 orderbook, trades, open interest etc. 
        channel: str
            channel subscribed
        
        '''
        self.subscriptions = defaultdict(set) 
        self.callbacks = {
            FUNDING: Callback(None),
            L2_BOOK: Callback(None),
            L3_BOOK: Callback(None),
            OPEN_INTEREST: Callback(None)
        }