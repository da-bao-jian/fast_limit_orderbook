'''
based on cryptofeed https://github.com/bmoscon/cryptofeed
'''
from collections import defaultdict
from typing import Union
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
            'funding': Callback(None),
            'callback': Callback(None),
            'l2': Callback(None),
            'level3': Callback(None),
            ''
        }