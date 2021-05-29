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
from .defines import L2_BOOK, BOOK_DELTA

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
        feed: class 
            all capital letters i.e. FTX, BYBIT
        '''
        self.loops.append((feed)) 

    def start_loops(self, start_loop: bool=True, exception_handler = None):
        '''
        start_loop: bool 
            event loop will not start if false
        '''
        if len(self.loops) == 0:
            text = "FH: No feed specified. Please specify at least one feed"
            LOG.critical(text)
            raise ValueError(text)

        loop = asyncio.get_event_loop()

        for feed in self.loops:
            # create task to the event loop
            feed.start_connection(loop)
        if not start_loop:
            return
        try:
            if exception_handler:
                loop.set_exception_handler(exception_handler)
            loop.run_forever()
        except SystemExit:
            LOG.info('FH: System exit received - shutting down')
        except KeyboardInterrupt:
            pass
        except Exception as why:
            LOG.exception('FH: Unhandled %r - shutting down', why)
        finally:
            # stop the feeds by shuting down the websocket, then close the asyncio event loop gracefully
            self.stop_feeds(loop=loop)
            self.close_loops(loop=loop)
        LOG.info('FH: leaving run()')
    
    def stop_feeds(self, loop=None):
        '''
        Terminate the feedhandler by tunning feedhanlder.running to False, then shutdown the feeds gracefully
        '''
        for feed in self.loops:
            # stop() method turns feedhandler.running to False
            feed.stop()
        
        shutdown_tasks = []
        if not loop:
            loop = asyncio.get_event_loop()
        LOG.info('FH: shudown connections handlers in feeds')
        for feed in self.loops:
            # close the ws
            task = loop.create_task(feed.shutdown())
            try:
                task.set_name(f'shudown {feed.id}')
            except AttributeError:
                pass 
            shutdown_tasks.append(task)
        loop.run_until_complete(asyncio.gather(*shutdown_tasks))
    
    def close_loops(self, loop=None):
        if not loop:
            loop = asyncio.get_event_loop()
        LOG.info('FH: stop the asynio loop')
        loop.stop()
        LOG.info('FH: run the Asyncio event loop one last time')
        # for the clean up, run the loop one last time
        loop.run_forever()

        pending = asyncio.all_tasks(loop=loop)
        LOG.info('FH: cancel the %s pending tasks',len(pending))
        for task in pending:
            task.cancel()
        LOG.info('FH: run the pending tasks if not sucessfully cancelled')
        loop.run_until_complete(asyncio.gather(*pending, loop=loop, return_exceptions=True))
        LOG.info('FH: close the event loop')
        loop.close()

if __name__ == '__main__':
    async def book(feed, symbol, book, timestamp, receipt_timestamp):
        print(f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Snapshot: {book}')
    async def delta(feed, symbol, delta, timestamp, receipt_timestamp):
        print(f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Delta: {delta}')
    f= Coinbase(symbols=['BTC-USD'], channels=[L2_BOOK], callbacks={BOOK_DELTA: delta, L2_BOOK: book})