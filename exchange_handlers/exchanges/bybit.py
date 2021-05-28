from ..feeds import Feed
from ..defines import BYBIT
class Bybit(Feed):
    id = BYBIT
    def __init__(self):
        super().__init__({'USD': 'wss://stream.bybit.com/realtime', 'USDT': 'wss://stream.bybit.com/realtime_public'}, **kwargs)
        self.SYMBOL_ENDPOINT = 'https://api.bybit.com/v2/public/symbols'




