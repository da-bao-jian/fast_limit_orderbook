import pytest
from ..lob import LimitOrderBook
from ..ob_tree.tree import LOBTree
from ..ob_tree.order import OrderLinkedlist, Order
import time

@pytest.fixture(scope='module')
def lob_instance():
    return LimitOrderBook()

@pytest.fixture
def lobtree_instance():
    return LOBTree()

@pytest.fixture
def orderll_instance():
    return OrderLinkedlist()

@pytest.fixture
def order_instance():
    return Order(10000, '123456', time.time(), 1.2, 'bid')


def test_process_order(lob_instance, order_instance):
    '''
    Test processing a single order           
    '''
    lob_instance.process_order(order_instance)
    assert isinstance(lob_instance.bid.limit_levels[order_instance.price], OrderLinkedlist) 
    assert lob_instance.bid.order_ids[order_instance.id] == order_instance.id
    assert lob_instance.bid.limit_levels[order_instance.price].volume == 1.2