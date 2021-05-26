from ..exchange_handlers.exchange_loop import ExchangeLoops
from ..exchange_handlers.feeds import Feed
from ..exchange_handlers.exchanges.coinbase import Coinbase
from ..exchange_handlers.exchanges.ftx import FTX
from ..exchange_handlers.exchanges.bybit import Bybit
from ..exchange_handlers.defines import L2_BOOK, BOOK_DELTA
import pytest

@pytest.fixture
def feed_instance():
    return Coinbase(), FTX(), Bybit()

def test_add_loop():
    exchange_loop = ExchangeLoops()
    exchange_loop.add_loop(feed_instance)
    assert len(exchange_loop.loop) == 2 

def test_feed_connection():
    feed = Coinbase(symbols=['BTC-USD'], channels=[L2_BOOK], callbacks={BOOK_DELTA: delta, L2_BOOK: book})
    feed.start_connection()