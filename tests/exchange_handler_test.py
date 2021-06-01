from ..exchange_handlers.exchange_loop import ExchangeLoops
from ..exchange_handlers.exchanges.coinbase import Coinbase
from ..exchange_handlers.exchanges.ftx import FTX
from ..exchange_handlers.exchanges.bybit import Bybit
from ..exchange_handlers.defines import L2_BOOK, BOOK_DELTA
from ..exchange_handlers.symbols_parser import Symbols
from ..exchange_handlers.connection_handler import ConnectionHandler
from ..exchange_handlers.connection import AsyncConnection
import pytest


@pytest.fixture(scope="module")
def coinbase_instance():
    async def book(feed, symbol, book, timestamp, receipt_timestamp):
        print(
            f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Snapshot: {book}')

    async def delta(feed, symbol, delta, timestamp, receipt_timestamp):
        print(
            f'Timestamp: {timestamp} Receipt Timestamp: {receipt_timestamp} Feed: {feed} Pair: {symbol} Delta: {delta}')

    return Coinbase(
        symbols=['BTC-USD'],
        channels=[L2_BOOK],
        callbacks={
            BOOK_DELTA: delta,
            L2_BOOK: book})


@pytest.fixture
def exchange_loop_instance():
    f = ExchangeLoops()
    return f


def test_coinbase_parse_symbol_data(coinbase_instance):
    symbols = Symbols
    assert symbols.populated('COINBASE')
    assert symbols.data['COINBASE']['normalized'] is not None


def test_event_loop_cycle(coinbase_instance, exchange_loop_instance):
    '''
    Test full event loop cycle, from initiation to termination
    '''
    exchange_loop_instance.add_loop(coinbase_instance)
    exchange_loop_instance.start_loops(testing=True)
    assert len(exchange_loop_instance.loops) != 0
    assert isinstance(exchange_loop_instance.loops[0], Coinbase)
    assert isinstance(coinbase_instance.connections[-1], ConnectionHandler)
    assert isinstance(coinbase_instance.connections[0].conn, AsyncConnection)
    assert coinbase_instance.subscription == {'level2': ['BTC-USD']}
    for conn in coinbase_instance.connections:
        assert conn.running == False


def test_no_feed_in_event_loop_error(exchange_loop_instance):
    with pytest.raises(ValueError):
        exchange_loop_instance.start_loops()


def test_close_loops(coinbase_instance, exchange_loop_instance):
    pass
