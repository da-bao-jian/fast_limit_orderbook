'''
FastAVLTree vs. FastRBTree vs. SortedDict performance test: http://www.grantjenks.com/docs/sortedcontainers/performance.html
Here, BST tree will only be used for set , remove and search; comparing to SortedDict, FastAVLTree and FastRBTree perform better 
in both methods. Additionally, search will be used less likely than set and remove, 
therefore maintaining a 'perfectly' balanced tree all the time is not necessary. In this regrard, RBTree beats AVLTree
as it requires less balancing. 
Hence, I chose to use FastRBTree over SortedDict and FastAVLTree, despite bintrees' halted development
'''
from bintrees import FastRBTree
from .orderlinkedlist import OrderLinkedlist
from .order import Order
import logging

LOG = logging.getLogger(__name__)

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
        # tree that store price as keys and number of orders on that level as values
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
    
    def _get_price(self, price):
        '''
        price: int 
        :return: OrderLinkedlist instance 

        '''
        return self.limit_levels[price]

    def insert_order(self, order: Order):
        '''
        order: Order Instance
            If order price doesn't exist in the self.limit_levels, insert it into the price level,
            else update accordingly;
            Will be used as limit order submission
        :return: None
        '''
        if order.id in self.order_ids:
            raise ValueError('order already exists in the book')
            return
        
        if order.price not in self.limit_levels:
            new_price_level = OrderLinkedlist()
            self.price_tree[order.price] = 1
            self.limit_levels[order.price] = new_price_level
            self.limit_levels[order.price].set_head(order)
            self.limit_levels[order.price].size += order.size
            self.order_ids[order.id] = order
            if self.max_price is None or order.price > self.max_price:
                self.max_price = order.price
            if self.min_price is None or order.price < self.min_price:
                self.min_price  = order.price 
        else:
            self.limit_levels[order.price].set_head(order)
            self.limit_levels[order.price].size += order.size
            self.order_ids[order.id] = order
            self.price_tree[order.price] += 1

    def update_existing_order(self, order_id: int, size: int):
        '''
        order_id: int
        size: int
            Update an existing order in a price level and its price level's size
        :return: None
        '''
        delta = self.order_ids[order_id].size - size
        try:
            self.order_ids[order_id].size = size
            order_price = self.order_ids[order_id].price
            # updated order will be put at the front of the list
            self.limit_levels[order_price].set_head(self.order_ids[order_id])
            self.limit_levels[order_price].size -= delta
        except Exception as e:
            LOG.info('Order is not in the book')


    def remove_order(self, order_id: int):
        '''
        order: Order Instance
            Remove the order from the self.order_ids first, 
            then remove it from the self.limit_levels;
            if the limit_levels is empty after removal, 
            adjust the max_price and min_price accordingly from the self.price_tree
        '''
        popped = self.order_ids.pop(order_id)
        self.limit_levels[popped.price].remove(popped, decrement=True)
        self.price_tree[popped.price] -= 1
        if self.limit_levels[popped.price].size == 0:
            self._remove_price_level(popped.price)

    def _remove_price_level(self, price: int):
        '''
        order: Order Instance
            Given a price level, remove the price level in the price_tree and limit_levels
            reset the max and min prices
        '''
        del self.limit_levels[price]
        self.price_tree.remove(price)
        if self.max_price == price:
            try:
                self.max_price = self.price_tree.max_key()
            except KeyError or ValueError:
                self.max_price = None 
        if self.min_price == price:
            try:
                self.min_price = self.price_tree.min_key()
            except KeyError or ValueError:
                self.min_price = None


    def market_order(self, order: Order):
        '''
        order: Order Instance
        '''
        if len(self.limit_levels) == 0:
            raise ValueError('No orders in the book')
            return
        
        if order.is_bid:
            best_price = self.min_price
            while order.size > 0 and best_price != None:
                price_level = self._get_price(best_price)
                order.size = price_level.consume_orders(order, self.order_ids)
                if self.limit_levels[price_level].size == 0:
                       self._remove_price_level(best_price)
                best_price = self.min_price
            if order.size != 0:
                LOG.warning('no more limit orders in the bid book')
        else:
            best_price = self.max_price
            while order.size > 0 and best_price != None:
                price_level = self._get_price(best_price)
                order.size = price_level.consume_orders(order, self.order_ids)
                if self.limit_levels[price_level].size == 0:
                       self._remove_price_level(best_price)
                best_price = self.max_price
            if order.size != 0:
                LOG.warning('no more orders in the ask book')
    
    def level_with_most_orders(self, range: int):
        '''
        range: int
            Gives the price level with the most orders on the top levels
        '''
        pass

    def iceberg(self):
        '''
        Iceberg order type
        '''
        pass