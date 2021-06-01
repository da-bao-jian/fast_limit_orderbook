class BSTnode(object):
    """
Representation of a node in a binary search tree.
Has a left child, right child, parent, and key value.
"""
    def __init__(self, t):
        self.key = t
        self.left = None
        self.right = None
        self.parent = None
        self.disconnect()
    def disconnect(self):
        self.left = None
        self.right = None
        self.parent = None


class BST(object):
    """
    Simple binary search tree implementation.
    This BST supports insert, find, and delete-min operations.
    Each tree contains some (possibly 0) BSTnode objects, representing nodes,
    and a pointer to the root.
    """

    def __init__(self):
        self.root = None

    def insert(self, t):
        """
        Insert key t into this BST, modifying it in-place. O(h)
        """
        new = BSTnode(t)
        if self.root is None:
            self.root = new
        else:
            node = self.root
            while True:
                if t < node.key:
                    if node.left is None:
                        node.left = new
                        new.parent = node
                        break
                    node = node.left
                else:
                    if node.right is None:
                        node.right = new
                        new.parent = node
                        break
                    node = node.right
        return new

    def find(self, t):
        """
        Return the node for key t if is in the tree, or None otherwise. O(h)
        """
        node = self.root
        while node is not None:
            if t == node.key:
                return node
            elif t < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def delete_min(self):
        """
        Delete the minimum key (and return the old node containing it).
        """
        if self.root is None:
            return None
        else:
            node = self.root
            while node.left is not None:
                node = node.left
            # remove that node and replace it with the right node
            if node.parent is not None:
                node.parent.left = node.right
            else: # if the node is the root node
                self.root = node.right
            if node.right is not None:
                node.right.parent = node.parent
            parent = node.parent
            node.disconnect()
            return node, parent

def _height(node):
    if node is None:
        return -1
    else:
        return node._height

def _update_height(node):
    node._height = max(_height(node.left), _height(node.right)) + 1

class AVL(BST):
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
        node = BST.insert(self, t)
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
        node, parent = BST.delete_min(self)
        self.rebalance(parent)

