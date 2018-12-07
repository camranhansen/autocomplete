"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple



################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type:
        the type of weight of the tree (avg, sum)
    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.weight = 0
        self.weight_type = weight_type
        self.subtrees = []
        self.value = []

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def __len__(self) -> int:
        """Returns the number of unique leaves in the tree"""

        if self.subtrees == [] and self.weight == 0 and self.value == []:
            return 0
        elif self.subtrees == [] and self.weight > 0:
            return 1
        else:
            s = 0
            for subtree in self.subtrees:
                s += subtree.__len__()
            return s

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert value into the autocompleter using helper,
        Then figure out weights/sorting
        See abstract class Autocompleter for representation invariants.
        >>> t = SimplePrefixTree('sum')
        >>> t.insert('cat', 2.0, ['c', 'a', 't'])
        >>> t.insert('car', 3.0, ['c', 'a', 'r'])
        >>> t.insert('dog', 4.0, ['d', 'o', 'g'])
        >>> len(t)
        3
        """
        dup = self.insert_helper(value, weight, prefix)
        self.update_weights(prefix, weight, dup)

        # for i in range(len(prefix)):
        #     self.auto_move(prefix[0:(len(prefix) - i)], 1, "rejig")
        # self.rejig_helper()
        # self.update_weights(prefix)

    def update_weights(self, prefix: List, weight: float, dup: bool):
        if self.weight_type == "sum":
            self.weight += weight
        else:
            if dup is True:
                self.weight = ((self.weight*self.__len__()) + weight)/self.__len__()
            else:
                if self.weight == 0:
                    self.weight = weight/self.__len__()
                else:
                    self.weight = ((self.weight*(self.__len__()-1)) + weight)/(self.__len__())
        for subtree in self.subtrees:
            relevant = prefix[0:len(self.value)+1]
            if subtree.value == relevant:
                subtree.update_weights(prefix, weight, dup)
                self.handle_sorting()

    def insert_helper(self, value: Any, weight: float, prefix: List) -> bool:
        """
        Insert value into autocompleter.
        """
        if len(prefix) == len(self.value):
            found = False
            for subtree in self.subtrees:
                if subtree.value == value:
                    subtree.weight += weight
                    return True
            if not found:
                new_leaf = SimplePrefixTree(self.weight_type)
                new_leaf.value = value
                new_leaf.weight = weight
                self.subtrees.append(new_leaf)
                return False

        else:
            found = False
            relevant = prefix[0:len(self.value) + 1]
            for subtree in self.subtrees:
                if subtree.value == relevant:

                    return subtree.insert_helper(value, weight, prefix)

            if not found:
                new_tree = SimplePrefixTree(self.weight_type)
                new_tree.value = relevant
                self.subtrees.append(new_tree)
                new_tree.insert_helper(value, weight, prefix)
            return False

    def handle_sorting(self) -> None:
        """
        Mutating helper to sort subtrees by weight
        in non-increasing weight order
        """
        self.subtrees.sort(key=lambda x: x.weight, reverse=True)

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """
        Function composed of two helpers.
        First helper checks if able to use all items in prefix.
        If able to continue without hitting any dead ends,
        Then helper 2 activates, giving leafs of the sub-tree.
        If limit is None, return all terminal nodes.
        Else, return values following greedy algorithm
        Under the assumption of sorted list implying largest values
        """

        if not prefix:
            r = self.getvalues(limit)
        else:
            r = self.auto_move(prefix, 1, "complete", limit)
        return sorted(r, key=lambda x: x[1], reverse=True)

    def auto_move(self, prefix: List, pos: int, move_type: str,
                  limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Helper function:
        Move to location where prefix is fulfilled in subtree
        Then call getvalues ro return a list of autocomplete values"""
        if pos == len(prefix) + 1:
            if move_type == "complete":
                return self.getvalues(limit)
        else:
            for subtree in self.subtrees:
                if subtree.value == prefix[0:pos]:
                    return subtree.auto_move(prefix, pos+1, move_type, limit)
            return []

    def getvalues(self, limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Get values < limit if it exists, else get everything"""
        r = []
        if not limit:
            for subtree in self.subtrees:
                if not subtree.subtrees:
                    r.append((subtree.value, subtree.weight))
                else:
                    r += (subtree.getvalues(limit))
            return r
        else:
            if limit == 0: # TODO does this work?
                return []
            for subtree in self.subtrees:
                if len(r) >= limit:
                    return r
                if not subtree.subtrees:
                    r.append((subtree.value, subtree.weight))
                else:
                    r += subtree.getvalues(limit - len(r))

            return r

    def remove(self, prefix: List) -> None:
        """
        Remove all nodes with prefix.
        Then, update the tree so it takes the removed node(s)
        Into account
        """
        if not prefix: # remove everything
            self.subtrees = []
            self.weight = 0
        else:
            self.remove_helper(prefix, 1)
            self.n_helper(prefix)
            self.weight_helper(prefix)

    def remove_helper(self, prefix, pos) -> None:
        if pos == len(prefix) + 1:
            self.subtrees = []
            self.weight = 0
            self.value = []
        else:
            for i in range(len(self.subtrees)):
                if self.subtrees[i].value == prefix[0:pos]:
                    self.subtrees[i].remove_helper(prefix, pos+1)
            self.handle_sorting()

    def n_helper(self, prefix):
        for subtree in self.subtrees:
            if subtree.__len__() == 0:
                self.subtrees.remove(subtree)
            elif subtree.value == prefix[0:len(self.value)+1]:
                subtree.n_helper(prefix)

    def weight_helper(self, prefix) -> None:
        self.weight = 0
        if self.weight_type == "sum":
            for subtree in self.subtrees:
                if subtree.value != prefix[0:len(self.value) + 1]:
                    self.weight += subtree.weight
                else:
                    subtree.weight_helper(prefix)
                    self.weight += subtree.weight

        else:
            n = 0
            w = 0
            for subtree in self.subtrees:
                if subtree.value != prefix[0:len(self.value) + 1]:
                    w += subtree.weight*subtree.__len__()
                    n += subtree.__len__()

                else:
                    subtree.weight_helper(prefix)
                    w += subtree.weight*subtree.__len__()
                    n += subtree.__len__()
            self.weight += w/n
        self.handle_sorting()







################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]


# if __name__ == '__main__':
#     import python_ta
#     python_ta.check_all(config={
#         'max-nested-blocks': 4
#     })
#     import doctest
#     doctest.testmod()
