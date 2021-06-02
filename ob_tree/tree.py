from bintrees import FastRBTree
from .order import OrderLinkedlist, Order
import logging

LOG = logging.getLogger('tree')

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
    
    def get_price(self, price):
        '''
        price: int 
        :return: OrderLinkedlist instance 
        '''
        return self.limit_levels[price]

    def insert_order(self, order):
        '''
        order: Order Instance
            If order price doesn't exist in the self.limit_levels, insert it into the price level,
            else update accordingly
        :return: None
        '''
        if order.price not in self.limit_levels:
            new_price_level = OrderLinkedlist()
            self.price_tree.insert(order.price, new_price_level)
            self.limit_levels[order.price] = new_price_level
            self.order_ids[order.id] = order
            if self.max_price is None or order.price > self.max_price:
                self.max_price = order.price
            if self.min_price is None or order.price < self.min_price:
                self.min_price  = order.price 
        else:
            self.limit_levels[order.price].set_tail(order)
            self.order_ids[order.id] = order
            # self.price_tree[order.price].set_tail(order)

    def update_existing_order(self, order):
        '''
        order: Order Instance
            Update an existing order in a price level and its price level's size
        :return: None
        '''
        delta = self.order_ids[order.id].size - order.size
        try:
            self.order_ids[order.id].size = order.size
        except Exception as e:
            LOG.info('Order is not in the book')
        self.price_tree[order.price].size -= delta


    def remove_order(self, order):
        '''
        order: Order Instance
            Remove the order from the self.order_ids first, 
            then remove it from the self.limit_levels;
            if the limit_levels is empty after removal, 
            adjust the max_price and min_price accordingly from the self.price_tree
        '''
        popped = self.order_ids.pop(order.id)
        self.limit_levels[order.price].remove(order)
        if self.limit_levels[popped.price].size == 0:
            self.price_tree.remove(popped.price)
            if self.max_price == popped.price:
                try:
                    self.max_price = self.price_tree.max_key()
                except KeyError or ValueError:
                    self.max_price = None 
            if self.min_price == popped.price:
                try:
                    self.min_price = self.price_tree.min_key()
                except KeyError or ValueError:
                    self.min_price = None
            
            


