'''
based on cryptofeed https://github.com/bmoscon/cryptofeed
'''
from ..feeds import Feed

class Coinbase(Feed):
    def __init__(self):
        super().__init__('wss://ftexchange.com/ws/', **kwargs)
        self.SYMBOL_ENDPOINT = 'https://api.pro.coinbase.com/products' 