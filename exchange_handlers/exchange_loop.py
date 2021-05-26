'''
based on cryptofeed https://github.com/bmoscon/cryptofeed
'''
from .logger import custom_logger
import asyncio
import uvloop
from .exchanges.bybit import Bybit
from .exchanges.coinbase import Coinbase
from .exchanges.ftx import FTX

mapping = {
    'FTX':FTX,
    'BYBIT':Bybit,
    'COINBASE':Coinbase,
}

class ExchangeLoops:
    '''
    This class monitors event loops 
    '''
    def __init__(self):
        self.loops = []
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
    def add_loop(self, feed):
        '''
        Add the exchange feed to the event loop
        feed: str 
            all capital letters i.e. FTX, BYBIT
        '''
        if isinstance(feed, str):
            if feed in mapping:
                self.loops.append((mapping[feed]()))
        else:
            raise ValueError("Invalid feed")
    
    def start_loops(self):
        return
    
    def stop_loops(self):
        return 

     