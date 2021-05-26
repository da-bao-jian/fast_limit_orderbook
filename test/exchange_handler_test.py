from ..exchange_handlers.exchange_loop import ExchangeLoops
from ..exchange_handlers.feeds import Feed
from ..exchange_handlers.exchanges.coinbase import Coinbase
from ..exchange_handlers.exchanges.ftx import FTX
from ..exchange_handlers.exchanges.bybit import Bybit
from ..exchange_handlers.defines import L2_BOOK, BOOK_DELTA
import pytest


@pytest.fixture
def coinbase_instance():
    async def book(feed, symbol, book, timestamp, receipt_timestamp):
        print(f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Snapshot: {book}')
    async def delta(feed, symbol, delta, timestamp, receipt_timestamp):
        print(f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Delta: {delta}')

    return Coinbase(symbols=['BTC-USD'], channels=[L2_BOOK], callbacks={BOOK_DELTA: delta, L2_BOOK: book})

def test_add_event_loop(coinbase_instance):
    exchange_loop = ExchangeLoops()
    exchange_loop.add_loop(coinbase_instance)
    assert len(exchange_loop.loop) == 2 

def test_feed_connection():
    feed.start_connection()