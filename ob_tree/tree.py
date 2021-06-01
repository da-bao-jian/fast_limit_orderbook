from bintrees import FastRBTree
from .order import OrderLinkedlist, Order

class LOBTree:

    def __init__(self):
        '''
        Limit order book tree implementation using Red-Black tree for self-balancing 
        Each limit price level is a OrderLinkedlist, and each order contains information 
        including id, price, timestamp, volume
        self.limit_level: dict
            key: price level; value: OrderLinkedlist object
        self.order_ids: dict  
            key: order id; value: Order object
            helps to locate order by id
        '''
        self.price_tree = FastRBTree()
        self.max_price = None  
        self.min_price = None
        self.limit_levels = {}
        self.order_ids = {}

    @property
    def max(self):
        return self.max
    
    @property
    def min(self):
        return self.min

    def insert(self, price):
        pass

    def remove(self):
        pass

