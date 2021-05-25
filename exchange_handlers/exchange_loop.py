from ..util import logger
import asyncio
import uvloop

class ExchangeLoops:
    '''
    This class monitors event loops 
    '''
    def __init__(self):
        self.loops = []
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
    def add_loop(self) -> None:
        return
    
    def start_loops(self) -> None:
        return
    
    def stop_loops(self) -> None:
        return 

     