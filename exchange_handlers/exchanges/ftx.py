from ..feeds import Feed

class FTX(Feed):
    def __init__(self):
        super().__init__('wss://ftexchange.com/ws/', **kwargs)
        self.SYMBOL_ENDPOINT = "https://ftx.com/api/markets"