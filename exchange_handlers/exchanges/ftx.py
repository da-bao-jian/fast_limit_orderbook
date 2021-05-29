from ..feeds import Feed
from ..defines import FTX
class FTX(Feed):
    id=FTX

    def __init__(self, callbacks=None, **kwargs):
        super().__init__('wss://ftexchange.com/ws/', callbacks=callbacks, **kwargs)
        self.SYMBOL_ENDPOINT = "https://ftx.com/api/markets"