from bintrees import FastRBTree

class LOBTree:

    def __init__(self):
        '''
        Limit order book tree implementation using Red-Black tree for self-balancing 
        Each limit price level is a OrderLinkedlist, and each order contains information 
        including id, price, timestamp, volume
        '''
        self.price_tree = FastRBTree()
        self.max = None  
        self.min = None

    @property
    def max(self):
        return self.max
    
    @property
    def min(self):
        return self.min

    def insert(self):
        pass

    def remove(self):
        pass

