from ..exchange_handlers.exchange_loop import ExchangeLoops
from ..exchange_handlers.exchanges.coinbase import Coinbase
from ..exchange_handlers.exchanges.ftx import FTX
from ..exchange_handlers.exchanges.bybit import Bybit
from ..exchange_handlers.defines import L2_BOOK, BOOK_DELTA
import pytest


@pytest.fixture(scope="module")
def coinbase_instance():
    async def book(feed, symbol, book, timestamp, receipt_timestamp):
        print(f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Snapshot: {book}')
    async def delta(feed, symbol, delta, timestamp, receipt_timestamp):
        print(f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Delta: {delta}')

    return Coinbase(symbols=['BTC-USD'], channels=[L2_BOOK], callbacks={BOOK_DELTA: delta, L2_BOOK: book})

@pytest.fixture(scope="module")
def exchange_loop_instance():
    f = ExchangeLoops()
    return f


def test_add_event_loop(coinbase_instance, exchange_loop_instance):
    exchange_loop_instance.add_loop(coinbase_instance) 
    assert len(exchange_loop_instance.loops) != 0 
