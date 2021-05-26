'''
based on cryptofeed https://github.com/bmoscon/cryptofeed
'''
from .logger import custom_logger
import asyncio
import uvloop

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
        feed: Feeds class instance 
            the exchange feed
        '''
        if isinstance(feed, str):
            self.loops.append(())
        return
    
    def start_loops(self):
        return
    
    def stop_loops(self):
        return 

     