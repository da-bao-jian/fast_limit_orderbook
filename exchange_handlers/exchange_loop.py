'''
based on cryptofeed https://github.com/bmoscon/cryptofeed/feed.py
'''
from .logger import custom_logger
import asyncio
import logging
from .defines import (FTX, BYBIT, COINBASE)
import uvloop
from .exchanges.bybit import Bybit
from .exchanges.coinbase import Coinbase
from .exchanges.ftx import FTX

mapping = {
    FTX:FTX,
    BYBIT:Bybit,
    COINBASE:Coinbase,
}

LOG = logging.getLogger('feedhandler')

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
    
    def start_loops(self, start_loop: bool=True, exception_handler = None):
        '''
        start_loop: bool 
            event loop will not start if false
        '''
        if len(self.loops) == 0:
            text = f'FH: No feed specified. Please specify at least one feed among {list(EXCHANGE_MAP.keys())}'
            LOG.critical(text)
            raise ValueError(text)

        loop = asyncio.get_event_loop()

        for feed in self.loops:
            # create task to the event loop
            feed.start(loop)
        if not start_loop:
            return

        try:
            if exception_handler:
                loop.set_exception_handler(exception_handler)
            loop.run_forever()
        except SystemExit:
            LOG.info('FH: System exit received - shutting down')
        except Exception as why:
            LOG.exception('FH: Unhandled %r - shutting down', why)
        finally:
            self.stop_loops(loop=loop)
            self.close_loops(loop=loop)
        LOG.info('FH: leaving run()')
    
    def stop_loops(self, loop=None):
        shutdown_tasks = []
        if not loop:
            loop = asyncio.get_event_loop()
        LOG.info('FH: shudown connections handlers in feeds')
        for feed in self.loops:
            task = loop.create_task(feed.shutdown())
            try:
                task.set_name(f'shudown {feed.id}')
            except AttributeError:
                pass 
            shutdown_tasks.append(task)
        loop.run_until_complete(asyncio.gather(*shutdown_tasks))
    
    def close_loops(self, loop=None):
