'''
WK Selph's Blogpost on "How to Build a Fast Limit Order Book"
https://web.archive.org/web/20110219163448/http://howtohft.wordpress.com/2011/02/15/how-to-build-a-fast-limit-order-book/

"There are three main operations that a limit order book (LOB) has to
implement: add, cancel, and execute.  The goal is to implement these
operations in O(1) time while making it possible for the trading model to
efficiently ask questions like “what are the best bid and offer?”, “how much
volume is there between prices A and B?” or “what is order X’s current
position in the book?”.

The vast majority of the activity in a book is usually made up of add and
cancel operations as market makers jockey for position, with executions a
distant third (in fact I would argue that the bulk of the useful information
on many stocks, particularly in the morning, is in the pattern of adds and
cancels, not executions, but that is a topic for another post).  An add
operation places an order at the end of a list of orders to be executed at
a particular limit price, a cancel operation removes an order from anywhere
in the book, and an execution removes an order from the inside of the book
(the inside of the book is defined as the oldest buy order at the highest
buying price and the oldest sell order at the lowest selling price).  Each
of these operations is keyed off an id number (Order.idNumber in the
pseudo-code below), making a hash table a natural structure for tracking
them.

Depending on the expected sparsity of the book (sparsity being the
average distance in cents between limits that have volume, which is
generally positively correlated with the instrument price), there are a
number of slightly different implementations I’ve used.  First it will help
to define a few objects:

    Order
      int idNumber;
      bool buyOrSell;
      int shares; // order size
      int limit;
      int entryTime;
      int eventTime;
      Order *nextOrder;
      Order *prevOrder;
      Limit *parentLimit;

    Limit  // representing a single limit price
      int limitPrice;
      int size;
      int totalVolume;
      Limit *parent;
      Limit *leftChild;
      Limit *rightChild;
      Order *headOrder;
      Order *tailOrder;

    Book
      Limit *buyTree;
      Limit *sellTree;
      Limit *lowestSell;
      Limit *highestBuy;

The idea is to have a binary tree of Limit objects sorted by limitPrice,
each of which is itself a doubly linked list of Order objects.  Each side
of the book, the buy Limits and the sell Limits, should be in separate trees
so that the inside of the book corresponds to the end and beginning of the
buy Limit tree and sell Limit tree, respectively.  Each order is also an
entry in a map keyed off idNumber, and each Limit is also an entry in a
map keyed off limitPrice.

With this structure you can easily implement these key operations with
good performance:

Add – O(log M) for the first order at a limit, O(1) for all others
Cancel – O(1)
Execute – O(1)
GetVolumeAtLimit – O(1)
GetBestBid/Offer – O(1)

where M is the number of price Limits (generally << N the number of orders).
Some strategy for keeping the limit tree balanced should be used because the
nature of markets is such that orders will be being removed from one side
of the tree as they’re being added to the other.  Keep in mind, though,
that it is important to be able to update Book.lowestSell/highestBuy
in O(1) time when a limit is deleted (which is why each Limit has a Limit
*parent) so that GetBestBid/Offer can remain O(1)."
'''

from .ob_tree.tree import LOBTree
from .ob_tree.order import Order

class LimitOrderBook:
    def __init__(self):
        self.bid = LOBTree()
        self.ask = LOBTree()
        self.best_bid = None
        self.best_ask = None

    def process_order(self, order: Order):
        '''
        Take in either a limit or market order; 
        if limit order's side is bid, add it to the bid book, else add it to the ask book;
        if market order's side is 'bid', match it against the ask book, else match it against the bid book
        '''
        if order.order_type == 'limit':
            if order.is_bid():
                if order.id not in self.bid.order_ids:
                    self.bid.insert_order(order)
                else:
                    raise ValueError('Order already in the list, please use "update" order')
            else:
                if order.id not in self.ask.order_ids:
                    self.ask.insert_order(order)
                else:
                    raise ValueError('Order already in the list, please use "update" order')
        elif order.order_type == 'market':
            if order.is_bid:
                self.ask.market_order(order)
            else:
                self.bid.market_order(order)
        elif order.order_type == 'update':
            if order.is_bid:
                self.update_order(order.id, 'bid')
            else:
                self.update_order(order.id, 'ask')

    
    def update_order(self, order_id: int, side: str):
        '''
        Given the order id and side, call the update_existing_order in that book
        '''
        if side == 'bid':
            self.bid.update_existing_order(order_id)
        else:
            self.ask.update_existing_order(order_id)