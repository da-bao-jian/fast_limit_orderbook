
class OrderLinkedlist:

    def __init__(self):
        self.volume = 0
        self.size = 0
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
        self.remove(order_to_insert, decrement=False)
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
        self.remove(order_to_insert, decrement=False)
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
            Used for cutting the line
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
			

    def remove_order_with_value(self, value):
        '''
        value: int
            Given value, remove the Order Instance
            Used for cancel order based on value
        '''
        order = self._head
        while order is not None:
            temp_node = order					
            order = order.next 
            if temp_node.value == value:
                self.remove(temp_node)


    def remove(self, order, decrement: bool=True):
        '''
        order: Order Instance
        decrement: bool
            decrement self.size when True
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
        if decrement:
            self.size -= order.size
            self.volume -= order.volume

    def containing_order(self, value):
        '''
        Search for an order given its value, return True if it's in the list, False otherwise
        O(n), n being number of orders in the OrderLinkedlist
        :return: bool
        '''
        order = self._head
        while order is not None and order.value != value:
            order = order.next
        return order is not None
	
    def _consume_orders(self, order, order_ids):
        '''
        order: Order Instance
        order_ids: dict | LOBTree.order_ids
            Eat up orders on this price level until either the order is fully executed or
            all of the orders on this level have exhausted
            There are three scenarios:
                1) tail order size is larger or equal to the order => delete order from order_ids, decrease the tail order size accordingly
                2) tail order size is smaller than the order and order size is smaller than price level total size
                    => keep taking the orders on this level until order.size is 0, decrease and delete the order from order_ids 
                3) order size is larger than all of the orders on this level => return order.size after deducting the order executed 
        :return: int, int
        '''
        # keeps a track of number of orders deleted to update the LOBTree.price_tree
        number_of_orders_deleted = 0
        while order.size > 0 and self.size > 0:
            # respecting time priority principle, orders on the same level follows FIFO design
            # since we add new orders at the head, we take orders out at the tail
            if self._tail.size >= order.size:
                self._tail.size -= order.size
                self.size -= order.size
                if self._tail.size == 0:
                    del order_ids[self._tail.id]
                    self.remove(self._tail)
                    number_of_orders_deleted += 1
                order.size = 0
                return order.size, number_of_orders_deleted
            else:
                order.size -= self._tail.size
                del order_ids[self._tail.id]
                self.remove(self._tail)
                number_of_orders_deleted += 1
        return order.size, number_of_orders_deleted

