from __future__ import annotations

from bisect import bisect
from typing import List

from hipscat.pixel_math import HealpixInputTypes, get_healpix_pixel
from hipscat.pixel_tree.pixel_node_type import PixelNodeType


class PixelNode:
    """A node in the HiPSCat quadtree of HEALPix pixels

    Attributes:
        node_type: If the node is a leaf, root, or inner type
        parent: The parent pixel node in the tree
        children: The child nodes of the pixel

    """

    _NODE_TYPE_MAX_CHILDREN = {
        PixelNodeType.ROOT: 12,
        PixelNodeType.INNER: 4,
        PixelNodeType.LEAF: 0,
    }

    def __init__(
        self,
        pixel: HealpixInputTypes,
        node_type: PixelNodeType,
        parent: PixelNode | None,
    ) -> None:
        """Inits PixelNode with its attributes

        Raises:
            ValueError: Invalid arguments for the specified pixel type
        """

        pixel = get_healpix_pixel(pixel)

        if node_type == PixelNodeType.ROOT:
            if parent is not None:
                raise ValueError("Root node cannot have a parent")
            if pixel.order != -1:
                raise ValueError("Root node must be at order -1")

        if node_type in (PixelNodeType.INNER, PixelNodeType.LEAF):
            if parent is None:
                raise ValueError("Inner and leaf nodes must have a parent")
            if pixel.order < 0 or pixel.pixel < 0:
                raise ValueError("Inner and leaf nodes must have an order and pixel number >= 0")

        if parent is not None and parent.hp_order != pixel.order - 1:
            raise ValueError("Parent node must be at order one less than current node")

        self.pixel = pixel
        self.node_type = node_type
        self.parent = parent
        self.children = []

        if self.parent is not None:
            self.parent.add_child_node(self)

    @property
    def hp_order(self):
        """The order of the HealpixPixel the node is at"""
        return self.pixel.order

    @property
    def hp_pixel(self):
        """The pixel number in NESTED ordering of the HealpixPixel the node is at"""
        return self.pixel.pixel

    def add_child_node(self, child: PixelNode):
        """Adds a child node to the node

        Maintains order of children based on pixel index

        Args:
            child: child node to add

        Raises:
            ValueError: The child to add does not have the current node set as a parent
            OverflowError: The node already has the maximum amount of children
        """
        if not child.parent == self:
            raise ValueError("Child node to add must have the node it is adding to as its parent")

        if len(self.children) >= self._NODE_TYPE_MAX_CHILDREN[self.node_type]:
            raise OverflowError("Node already has the maximum amount of children")

        insert_index = bisect(list(map(lambda node: node.hp_pixel, self.children)), child.hp_pixel)
        self.children.insert(insert_index, child)

    def remove_child_link(self, node):
        """Remove a link to a child node from the node. This removes it from the list of children,
        but does not delete the node

        Args:
            node: the node object to remove
        """
        if node not in self.children:
            raise ValueError("Node not a child node, cannot remove")
        self.children.remove(node)

    def get_all_leaf_descendants(self) -> List[PixelNode]:
        """Gets all descendant nodes that are leaf nodes.

        Leafs nodes correspond to pixels that have data files containing astronomical objects, so
        this method is used to get the files containing all astronomical objects within the pixel.

        This function called on a leaf node returns a list including the node itself and only itself

        Returns:
            A list containing all leaf nodes that descend from the current node
        """

        leaf_descendants = []
        self._add_all_leaf_descendants_rec(leaf_descendants)
        return leaf_descendants

    def _add_all_leaf_descendants_rec(self, leaf_descendants: List[PixelNode]):
        """Recursively add all leaf descendants to list

        list must be created outside function, done for efficiency vs list concat
        """
        if self.node_type == PixelNodeType.LEAF:
            leaf_descendants.append(self)

        for child in self.children:
            # pylint: disable=protected-access
            child._add_all_leaf_descendants_rec(leaf_descendants)
