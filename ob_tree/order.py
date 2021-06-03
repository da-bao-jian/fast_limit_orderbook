class Order:
    def __init__(self, price: int, id: int, order_type: str, timestamp: int, size: int, side: str):
        self.id = id
        self.timestamp = timestamp
        self.side = side
        self.size = size
        self.order_type = order_type
        # if market order, then it adds no depth to the book
        if self.order_type == 'market':
            self.price = None
        else:
            self.price = price
        self.prev = None
        self.next = None
        self.volume = self.size * self.price

    def is_bid(self):
        '''
        Return true is order is bid, otherwise false
        :return: bool
        '''
        return self.side == 'bid'
