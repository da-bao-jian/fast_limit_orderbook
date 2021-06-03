import pytest
from ..lob import LimitOrderBook
from ..ob_tree.tree import LOBTree
from ..ob_tree.order import Order
from ..ob_tree.orderlinkedlist import OrderLinkedlist
import time
import random

@pytest.fixture(scope='module')
def lob_instance():
    return LimitOrderBook()

@pytest.fixture
def lobtree_instance():
    return LOBTree()

@pytest.fixture
def orderll_instance():
    return OrderLinkedlist()

@pytest.fixture()
def order_instances_factory():
    '''
    Pytest factory function that randomly generate Order instances each time it's being called
    '''
    price = random.randint(10000, 10100)
    id = random.randint(100000,999999)
    order_type = 'limit'
    timestamp = time.time()
    size = round(random.uniform(0.5, 2.5), 4)
    side = ['bid', 'ask'][random.randrange(2)]
    def _orders():
        return Order(price=price, id=id, order_type=order_type, timestamp=timestamp, size=size, side=side)
    return _orders

def test_process_order(lob_instance, order_instance):
    '''
    Test processing a single order           
    '''
    lob_instance.process_order(order_instance)
    assert isinstance(lob_instance.bid.limit_levels[order_instance.price], OrderLinkedlist) 
    assert lob_instance.bid.order_ids[order_instance.id] == order_instance.id
    assert lob_instance.bid.limit_levels[order_instance.price].volume == 1.2