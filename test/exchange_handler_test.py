from ..exchange_handlers.exchange_loop import ExchangeLoops
from ..exchange_handlers.feeds import Feed
import pytest

@pytest.fixture
def feed_instance():
    return Coinbase(), FTX()

def test_add_loop():
    exchange_loop = ExchangeLoops()
    exchange_loop.add_loop(feed_instance)
    assert len(exchange_loop.loop) == 2 

