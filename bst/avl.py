import bst

def _height(node):
    if node is None:
        return -1
    else:
        return node._height

def _update_height(node):
    node._height = max(_height(node.left), _height(node.right)) + 1

class AVL(bst.BST):
    """
    AVL binary search tree.
    Insert, find, and delete-min operations in O(log N) time.
    """
    def _left_rotate(self, x):
        '''
        Reference: Introduction to Algorithms Chapter 13.2
        '''
        y = x.right
        y.parent = x.parent
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left is x:
                y.parent.left = y
            elif y.parent.right is x:
                y.parent.right = y
        x.right = y.left
        if x.right is not None:
            x.right.parent = x
        y.left = x
        x.parent = y
        _update_height(x)
        _update_height(y)

    def _right_rotate(self, x):
        '''
        Reference: Introduction to Algorithms, Chapter 13.2
        '''
        y = x.left
        y.parent = x.parent
        if y.parent is None:
            self.root = y
        else:
            if y.parent.left is x:
                y.parent.left = y
            elif y.parent.right is x:
                y.parent.right = y
        x.left = y.right
        if x.left is not None:
            x.left.parent = x
        y.right = x
        x.parent = y
        _update_height(x)
        _update_height(y)

    def insert(self, t):
        """Insert key t into this tree, modifying it in-place."""
        node = bst.BST.insert(self, t)
        self.rebalance(node)

    def rebalance(self, node):
        while node is not None:
            _update_height(node)
            if _height(node.left) >= 2 + _height(node.right):
                if _height(node.left.left) >= _height(node.left.right):
                    self._right_rotate(node)
                else:
                    self._left_rotate(node.left)
                    self._right_rotate(node)
            elif _height(node.right) >= 2 + _height(node.left):
                if _height(node.right.right) >= _height(node.right.left):
                    self._left_rotate(node)
                else:
                    self._right_rotate(node.right)
                    self._left_rotate(node)
            node = node.parent

    def delete_min(self):
        node, parent = bst.BST.delete_min(self)
        self.rebalance(parent)

