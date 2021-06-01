
from logging import setLogRecordFactory


class OrderLinkedlist:
    def __init__(self):
        self.total_volume = 0
        self._head = None
        self._tail = None




class Order:
    def __init__(self, price, id, timestamp, size, type):
        self.price = price
        self.id = id
        self.timestamp = timestamp
        self.size = size
        self.type = type