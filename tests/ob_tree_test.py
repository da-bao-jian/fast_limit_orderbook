import pytest
from ..lob import LimitOrderBook
from ..ob_tree.tree import LOBTree
from ..ob_tree.order import Order
from ..ob_tree.orderlinkedlist import OrderLinkedlist
import time
import random

@pytest.fixture(scope='module')
def lob_instance():
    '''
    To test the whole cycle
    '''
    return LimitOrderBook()

@pytest.fixture(scope='module')
def lobtree_instance():
    '''
    To test individual functions in isolation
    '''
    return LOBTree()

@pytest.fixture(scope='module')
def orderll_instance():
    return OrderLinkedlist()

@pytest.fixture
def single_order_instance_factory(**kwargs):
    def _single_order(**kwargs):
        return Order(order_type = 'limit', side = 'bid', **kwargs)
    return _single_order

@pytest.fixture()
def order_instances_factory():
    '''
    Pytest factory function that randomly generate Order instances 
    Mainly used for filling the orderbook
    '''
    def _orders(id):
        price = random.randint(10000, 10100)
        order_type = 'limit'
        timestamp = time.time()
        size = round(random.uniform(0.5, 2.5), 4)
        side = ['bid', 'ask'][random.randrange(2)]
        return Order(price=price, id=id, order_type=order_type, timestamp=timestamp, size=size, side=side)
    return _orders

def test_insert_order_function(lobtree_instance, single_order_instance_factory):
    lobtree_instance.insert_order(single_order_instance_factory(price=10000, id=101011,  timestamp=time.time(), size=1000, ))
    lobtree_instance.insert_order(single_order_instance_factory(price=10002, id=101012,  timestamp=time.time(), size=1000, ))
    lobtree_instance.insert_order(single_order_instance_factory(price=10001, id=101013,  timestamp=time.time(), size=1000, ))
    lobtree_instance.insert_order(single_order_instance_factory(price=10001, id=101014,  timestamp=time.time(), size=1000, ))
    # test tree levels
    assert lobtree_instance.price_tree[10001] == 2
    # test limit_level 
    assert len(lobtree_instance.limit_levels) == 3
    assert lobtree_instance.order_ids[101011].price == 10000
    assert lobtree_instance.order_ids[101012] != None
    # test FIFO structure of the OrderLinkedList
    assert lobtree_instance.limit_levels[10001]._head.id == 101014
    assert lobtree_instance.limit_levels[10001]._tail.id == 101013
    assert lobtree_instance.limit_levels[10001].size == 2000
    assert lobtree_instance.max_price == 10002
    assert lobtree_instance.min_price == 10000
    with pytest.raises(ValueError):
        lobtree_instance.insert_order(single_order_instance_factory(price=10010, id=101011,  timestamp=time.time(), size=1000,))
    assert lobtree_instance.order_ids[101011].price == 10000


def test__order_function(lobtree_instance):
    lobtree_instance.update_existing_order_size(101013, 1010)
    assert lobtree_instance.order_ids[101013].size == 1010
    assert lobtree_instance.limit_levels[10001].size == 2010
    assert lobtree_instance.limit_levels[10001]._head.id == 101013

def test_remove_order_function(lobtree_instance):
    lobtree_instance.remove_order(101013)
    lobtree_instance.remove_order(101012)
    assert 101013 not in lobtree_instance.order_ids
    assert lobtree_instance.limit_levels[10001].size == 1000
    assert lobtree_instance.price_tree[10001] == 1
    assert lobtree_instance.limit_levels[10001]._tail.id == 101014 
    assert lobtree_instance.limit_levels[10001]._head.id == 101014 
    assert lobtree_instance.price_tree[10001] == 1
    assert lobtree_instance.max_price == 10001
    assert lobtree_instance.min_price == 10000
    assert 10002 not in lobtree_instance.price_tree
    assert 10002 not in lobtree_instance.limit_levels

#################################################################################################################################
# whole book test

def test_process_limit_order(lob_instance, order_instances_factory):
    '''
    Randomly prefill the ordrebook with 1000 orders, and test each level of limit_level agasint price_tree 
    '''
    # generating 1000 unique six-digit id numbers
    global rand_id 
    rand_id = random.sample(range(100000,999999), 1000)
    for i in range(1000):
        lob_instance.process_order(order_instances_factory(rand_id[i]))
    for level in lob_instance.ask.limit_levels:
        assert level in lob_instance.ask.price_tree
    for level in lob_instance.bid.limit_levels:
        assert level in lob_instance.bid.price_tree

def test_update_order(lob_instance):
    # fetch the order that needs to be updated, here I conviniently pick the first one in the rand_id list
    if rand_id[0] in lob_instance.bid.order_ids: 
        order_need_update = lob_instance.bid.order_ids[rand_id[0]]
    else:
        order_need_update = lob_instance.ask.order_ids[rand_id[0]]
    
    # change the size to 3, which is larger than all of the order sizes in the book 
    if order_need_update.is_bid():
        lob_instance.update_order(order_need_update.id, 'bid', 3, 20000)
        assert lob_instance.bid.max_price == 20000
        assert 20000 in lob_instance.bid.price_tree
        assert 20000 in lob_instance.bid.limit_levels
        assert lob_instance.bid.limit_levels[20000].size == 3
        assert rand_id[0] in lob_instance.bid.order_ids
        new_price_level = list(lob_instance.bid.limit_levels)[3]
        lob_instance.update_order(order_need_update.id, 'bid', new_price = new_price_level, change_size = False)
        assert lob_instance.bid.max_price != 20000
        assert 20000 not in lob_instance.bid.price_tree
        assert 20000 not in lob_instance.bid.limit_levels
        assert lob_instance.bid.limit_levels[new_price_level]._head.id == order_need_update.id
    else: 
        lob_instance.update_order(order_need_update.id, 'ask', 3, 20000)
        assert lob_instance.ask.max_price == 20000
        assert 20000 in lob_instance.ask.price_tree
        assert 20000 in lob_instance.ask.limit_levels
        assert lob_instance.ask.limit_levels[20000].size == 3
        assert rand_id[0] in lob_instance.ask.order_ids
        new_price_level = list(lob_instance.ask.limit_levels)[3]
        lob_instance.update_order(order_need_update.id, 'ask', new_price = new_price_level, change_size = False)
        assert lob_instance.ask.max_price != 20000
        assert 20000 not in lob_instance.ask.price_tree
        assert 20000 not in lob_instance.ask.limit_levels
        assert lob_instance.ask.limit_levels[new_price_level]._head.id == order_need_update.id

    

def test_market_order(lobtree_instance, order_instances_factory):
    pass


# def test_process_order(lob_instance, order_instance):
#     '''
#     Test processing a single order           
#     '''
#     lob_instance.process_order(order_instance)
#     assert isinstance(lob_instance.bid.limit_levels[order_instance.price], OrderLinkedlist) 
#     assert lob_instance.bid.order_ids[order_instance.id] == order_instance.id
#     assert lob_instance.bid.limit_levels[order_instance.price].volume == 1.2