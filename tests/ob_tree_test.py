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

@pytest.fixture(scope='module')
def lobtree_instance():
    return LOBTree()

@pytest.fixture(scope='module')
def orderll_instance():
    return OrderLinkedlist()

@pytest.fixture(scope='module')
def single_order_instance_factory(**kwargs):
    def _single_order(**kwargs):
        return Order(**kwargs)
    return _single_order

@pytest.fixture()
def order_instances_factory():
    '''
    Pytest factory function that randomly generate Order instances 
    Mainly used for filling the orderbook
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

def test_insert_order_function(lobtree_instance, single_order_instance_factory):
    lobtree_instance.insert_order(single_order_instance_factory(price=10000, id=101011, order_type='limit', timestamp=time.time(), size=1000, side='bid'))
    lobtree_instance.insert_order(single_order_instance_factory(price=10002, id=101012, order_type='limit', timestamp=time.time(), size=1000, side='bid'))
    lobtree_instance.insert_order(single_order_instance_factory(price=10001, id=101013, order_type='limit', timestamp=time.time(), size=1000, side='bid'))
    lobtree_instance.insert_order(single_order_instance_factory(price=10001, id=101014, order_type='limit', timestamp=time.time(), size=1000, side='bid'))
    # test tree levels
    assert lobtree_instance.price_tree[10001] == 2
    # test limit_level 
    assert len(lobtree_instance.limit_levels) == 3
    assert lobtree_instance.order_ids[101011].price == 10000
    assert lobtree_instance.order_ids[101012] != None
    # test FIFO structure of the OrderLinkedList
    assert lobtree_instance.limit_levels[10001]._head.id == 101014
    assert lobtree_instance.limit_levels[10001]._tail.id == 101013
    assert lobtree_instance.max_price == 10002
    assert lobtree_instance.min_price == 10000
    

def test_insert_order_function_exception(lobtree_instance, single_order_instance_factory):
    with pytest.raises(ValueError):
        lobtree_instance.insert_order(single_order_instance_factory(price=10010, id=101011, order_type='limit', timestamp=time.time(), size=1000, side='bid'))
    assert lobtree_instance.order_ids[101011].price == 10000


# def test_process_order(lob_instance, order_instance):
#     '''
#     Test processing a single order           
#     '''
#     lob_instance.process_order(order_instance)
#     assert isinstance(lob_instance.bid.limit_levels[order_instance.price], OrderLinkedlist) 
#     assert lob_instance.bid.order_ids[order_instance.id] == order_instance.id
#     assert lob_instance.bid.limit_levels[order_instance.price].volume == 1.2