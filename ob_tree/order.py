
class OrderLinkedlist:

    def __init__(self):
        self.total_volume = 0
        self._head = None
        self._tail = None

    def set_head(self, order):
        '''
        order: Order Instance
            if _head is None, set _head and _tail to order 
            else insert before the _head
            O(1)
        '''
        if self._head is None:
            self._head = order
            self._tail= order
            return
        self.insert_before(self._head, order)
		
    def set_tail(self, order):
        '''
        order: Order Instance
            if _tail is None, set _head and _tail to order 
            else insert after the _tail
            O(1)
        '''
        if self._tail is None:
            self._head = order
            self._tail= order
            return
        self.insert_after(self._tail, order)

    def insert_before(self, order, order_to_insert):
        '''
        order: Order Instance
        order_to_insert: Order Instance
            Function used in set_head and insert_at_position method
            O(1)
        '''
        if order_to_insert == self._head and order_to_insert == self._tail:
            return
        self.remove(order_to_insert)
        if order != self._head:			
            order_to_insert = order.prev			
            order_to_insert = order
            order.prev.next = order_to_insert
            order.prev = order_to_insert
        else:			
            order_to_insert.prev = order.prev			
            order_to_insert.next = order
            self._head = order_to_insert
            order.prev = order_to_insert
		
    def insert_after(self, order, order_to_insert):
        '''
        order: Order Instance
        order_to_insert: Order Instance
            Function used in set_tail  
            O(1)
        '''
        if order_to_insert == self._head and order_to_insert == self._tail:
            return
        self.remove(order_to_insert)
        if order != self._tail:			
            order_to_insert.prev = order			
            order_to_insert.next = order.next
            order.next.prev = order_to_insert
            order.next = order_to_insert
        else:			
            order_to_insert.prev = order			
            order_to_insert.next = order.next
            self._tail = order_to_insert
            order.next = order_to_insert
			
    def insert_at_position(self, position, order_to_insert):
        '''
        position: int 
        order_to_insert: Order Instance
            Given a position, insert the order
            O(1)
        '''
        if position == 1:
            self.set_head(order_to_insert)
            return
        order = self._head
        current = 1
        while order is not None and current != position:
            current += 1
            order = order.next
        if order is None:
            self.set_tail(order_to_insert)
        else:
            self.insert_before(order, order_to_insert)
			

    # def remove_order_with_value(self, value):
    #     '''
    #     value
    #     Given value, remove the Order Instance
    #     '''
    #     order = self._head
    #     while order is not None:
    #         temp_node = order					
    #         order = order.next 
    #         if temp_node.value == value:
    #             self.remove(temp_node)


    def remove(self, order):
        '''
        order: Order Instance
            Remove given order
            O(1)
        '''
        if order == self._head:
            self._head = self._head.next
        if order == self._tail:
            self._tail = self._tail.prev
        if order.prev is not None: 
            order.prev.next = order.next
        if order.next is not None:
            order.next.prev = order.prev
        order.prev = None
        order.next = None

    def containing_order(self, value) -> bool:
        '''
        Search for an order given its value, return True if it's in the list, False otherwise
        '''
        order = self._head
        while order is not None and order.value != value:
            order = order.next
        return order is not None
	
	

class Order:
    def __init__(self, price, id, timestamp, size, side):
        self.price = price
        self.id = id
        self.timestamp = timestamp
        self.side = side
        self.type = type
        self.prev = None
        self.next = None