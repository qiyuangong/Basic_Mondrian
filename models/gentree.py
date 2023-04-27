#!/usr/bin/env python
# coding=utf-8

# logic tree

from typing import Dict, List


class GenTree(object):

    """Class for Generalization hierarchies (Taxonomy Tree).
    Store tree node in instances.
    self.value: node value
    self.level: tree level (top is 0)
    self.leaf_num: number of leaf node covered
    self.parent: ancestor node list
    self.child: direct successor node list
    self.cover: all nodes covered by current node
    """

    def __init__(self, value=None, parent=None, isleaf=False):
        self.value = ''
        self.level = 0
        self.leaf_num = 0
        self.parents: List[GenTree] = []
        self.children: List[GenTree] = []
        self.cover: Dict[str, GenTree] = {}

        if value is not None:
            self.value = value
            self.cover[value] = self

        if parent is not None:
            self.parents = parent.parents[:]
            self.parents.insert(0, parent)
            parent.children.append(self)
            self.level = parent.level + 1
            for node in self.parents:
                node.cover[self.value] = self
                if isleaf:
                    node.leaf_num += 1

    def node(self, value: str):
        """Search tree with value, return GenTree node.
        return point to that node, or None if not exists
        """
        try:
            return self.cover[value]
        except:
            return None

    def __len__(self):
        """
        return number of leaf node covered by current node
        """
        return self.leaf_num
