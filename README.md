## Data Structure
Orderbook data strucuture is based on WK Selph's Blogpost on ["How to Build a Fast Limit Order Book"](https://web.archive.org/web/20110219163448/http://howtohft.wordpress.com/2011/02/15/how-to-build-a-fast-limit-order-book/):

* Bid/ask books are Red-Black Trees;
* Each tree has an object for storing order ids and an object for storing price levels
* Each price level is a doubly linked list that implements FIFO pattern for Price-Time-Priority order matching;
* Different from WK Selph's design, add and cancel order will be O(log N) time since tree balancing mechanism is used. 



## References
[Order Book Programming Problem](https://web.archive.org/web/20161116104649/http://rgmadvisors.com/problems/orderbook/)

[QuantCup's winning submission](https://web.archive.org/web/20141222151051/https://dl.dropboxusercontent.com/u/3001534/engine.c)
