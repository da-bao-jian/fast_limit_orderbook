# Fast Limit Order Book Simulator

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9fb9226023cb4f73b00a2bdbe9ff09ef)](https://app.codacy.com/gh/dabaojian1992/fast_limit_orderbook?utm_source=github.com&utm_medium=referral&utm_content=dabaojian1992/fast_limit_orderbook&utm_campaign=Badge_Grade_Settings)

Orderbook Simulator that supports limit and market orders

This algorithm runs Python 3.9+. If you have pipenv, install it by 
```
pipenv install
```

To run the test, 
```
python3 pytest tests/ob_tree_test.py
```

## Data Structure
Orderbook data strucuture is based on WK Selph's Blogpost on ["How to Build a Fast Limit Order Book"](https://web.archive.org/web/20110219163448/http://howtohft.wordpress.com/2011/02/15/how-to-build-a-fast-limit-order-book/):

* Bid/ask books are Red-Black Trees;
* Each tree has an object for storing order ids and an object for storing price levels
* Each price level is a doubly linked list that implements FIFO pattern for Price-Time-Priority order matching;
* Different from WK Selph's design, add and cancel order will be O(log N) time since tree balancing mechanism is used. 



## References
[Order Book Programming Problem](https://web.archive.org/web/20161116104649/http://rgmadvisors.com/problems/orderbook/)

[QuantCup's winning submission](https://web.archive.org/web/20141222151051/https://dl.dropboxusercontent.com/u/3001534/engine.c)
