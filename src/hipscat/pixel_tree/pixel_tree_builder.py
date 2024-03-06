# pylint: disable=duplicate-code

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.healpix_pixel import get_lower_order_pixel, get_higher_order_pixels
from hipscat.pixel_math.healpix_pixel_convertor import HealpixInputTypes, get_healpix_pixel, get_healpix_tuple
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree


class PixelTreeBuilder:
    """Build a PixelTree

    Initially a root node is created when the builder is initialized.
    Nodes can then be added to the tree.
    To create a pixel tree object once the tree is built, call the `build` method

    """

    def __init__(self):
        self.pixels = {-1: {-1: PixelNodeType.ROOT}}

    def build(self) -> PixelTree:
        """Build a `PixelTree` object from the nodes created

        Returns:
            The pixel tree with the nodes created in the builder
        """
        return PixelTree(self.pixels)

    @staticmethod
    def from_healpix(healpix_pixels: List[HealpixInputTypes]) -> PixelTree:
        """Build a tree from a list of constituent healpix pixels

        Args:
            healpix_pixels: list of healpix pixels

        Returns:
            The pixel tree with the leaf pixels specified in the list
        """
        pixel_tuples = [get_healpix_tuple(p) for p in healpix_pixels]
        pixel_array = np.array(pixel_tuples).T
        orders = pixel_array[0]
        pixels = pixel_array[1]
        max_order = np.max(orders)
        starts = pixels * 4**(max_order - orders)
        ends = (pixels + 1) * 4**(max_order - orders)
        # array = np.vectorize(get_healpix_tuple)(healpix_pixels)
        result = np.vstack((starts, ends)).T
        result.sort(axis=0)
        return PixelTree(result)

    def contains(self, pixel: HealpixInputTypes) -> bool:
        """Check if tree contains a node at a given order and pixel

        Args:
            pixel: HEALPix pixel to check. Either of type `HealpixPixel`
                or a tuple of (order, pixel)

        Returns:
            True if the tree contains the pixel, False if not
        """
        (order, pixel) = get_healpix_tuple(pixel)
        return order in self.pixels and pixel in self.pixels[order]

    def __contains__(self, item):
        return self.contains(item)

    def get_node_type(self, pixel: HealpixInputTypes) -> PixelNodeType | None:
        """Get the node at a given pixel

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)

        Returns:
            The PixelNode at the index, or None if a node does not exist
        """
        (order, pixel) = get_healpix_tuple(pixel)
        if self.contains((order, pixel)):
            return self.pixels[order][pixel]
        return None

    def __getitem__(self, item):
        return self.get_node_type(item)

    def create_node_and_parent_if_not_exist(self, pixel: HealpixInputTypes, node_type: PixelNodeType):
        """Creates a node and adds to `self.pixels` in the tree, and recursively creates parent
        node if parent does not exist

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
        """
        order, pixel = get_healpix_tuple(pixel)
        if self.contains((order, pixel)):
            raise ValueError("Incorrectly configured catalog: catalog contains duplicate pixels")

        if order == 0:
            self.create_node((order, pixel), node_type)
            return

        parents_to_add = []
        for delta_order in range(1, order + 1):
            parent_order = order - delta_order
            parent_pixel = get_lower_order_pixel(order, pixel, delta_order)
            if not self.contains((parent_order, parent_pixel)):
                parents_to_add.insert(0, (parent_order, parent_pixel))
            else:
                break

        for add_order, add_pixel in parents_to_add:
            self.create_node(
                (add_order, add_pixel), PixelNodeType.INNER
            )

        self.create_node((order, pixel), node_type)

    def create_node(
        self,
        pixel: HealpixInputTypes,
        node_type: PixelNodeType,
        replace_existing_node=False,
        check_parent=True
    ):
        """Create a node and add to `self.pixels` in the tree

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
            replace_existing_node: (Default: False) If True and node at `pixel` already exists,
                the existing node will be removed and replaced with the new node.
            check_parent (bool): (Default: True) If True, will check if a parent node already exists at the
                correct order and pixel and the correct node_type, and raise an error if not
        """
        order, pixel = get_healpix_tuple(pixel)
        if order < 0:
            raise ValueError("Cannot create node, order must be >= 0")
        if check_parent and order > 0:
            parent_pixel = (order - 1, get_lower_order_pixel(order, pixel, 1))
            if parent_pixel not in self or self[parent_pixel] == PixelNodeType.LEAF:
                raise ValueError(
                    f"Cannot create node at {str((order, pixel))}, "
                    f"parent node at {str(parent_pixel)} is invalid"
                )
        if (order, pixel) in self:
            if not replace_existing_node:
                raise ValueError(f"Cannot create node at {str(pixel)}, node already exists")
        if order not in self.pixels:
            self.pixels[order] = {}
        self.pixels[order][pixel] = node_type

    def remove_node(self, pixel: HealpixInputTypes):
        """Remove node in tree

        Removes a node at a specified pixel in the tree. Raises a `ValueError` if no node at
        specified pixel.

        Args:
            pixel: HEALPix pixel to remove the node at

        Raises:
            ValueError: No node in tree at pixel
        """
        order, pixel = get_healpix_tuple(pixel)
        if (order, pixel) not in self:
            raise ValueError(f"No node at pixel {str((order, pixel))}")
        self._remove_node_and_children_from_tree(order, pixel)

    def _remove_node_and_children_from_tree(self, order: int, pixel: int):
        node = self.pixels[order].pop(pixel)
        if len(self.pixels[order]) == 0:
            self.pixels.pop(order)
        for child_pixel in get_higher_order_pixels(order, pixel, 1):
            if (order + 1, child_pixel) in self:
                self._remove_node_and_children_from_tree(order + 1, child_pixel)

    def _get_tree_and_pixel_from_node(self, node: PixelNode | Tuple[HealpixInputTypes, PixelTree]) -> Tuple[HealpixInputTypes, PixelTree]:
        pixel = None
        tree = None
        if isinstance(node, PixelNode):
            pixel = (node.pixel.order, node.pixel.pixel)
            tree = node.tree
        elif isinstance(node, tuple):
            pixel = get_healpix_tuple(node[0])
            tree = node[1]
        else:
            raise ValueError("node or pixel and tree must be not none")
        return pixel, tree

    def add_all_descendants_from_node(
            self, node: PixelNode | Tuple[HealpixInputTypes, PixelTree]
    ):
        """Adds all descendents from a given node to the current tree

        Used to make the current tree being built mirror the subtree from the specified node in
        another tree.

        A node at the specified position must exist in the current tree with the correct node type.

        Args:
            node: The node from another tree to match

        Raises:
            ValueError: No node exists in the current tree at the same location as the specified
            node
        """
        other_pixel, other_tree = self._get_tree_and_pixel_from_node(node)
        if other_pixel not in self:
            raise ValueError("No node in tree matching given node")
        child_pixels = other_tree.get_child_pixels(other_pixel)
        while len(child_pixels) > 0:
            pixel = child_pixels.pop(0)
            child_pixels += other_tree.get_child_pixels(pixel)
            self.create_node(pixel, other_tree.get_node_type(pixel))

    def split_leaf_to_match_partitioning(self, node_to_match: PixelNode | Tuple[HealpixInputTypes, PixelTree]):
        """Split a given leaf node into higher order nodes to match another node's partitioning

        Args:
            node_to_match: The node in another tree to match the partitioning of

        Raises:
            ValueError if no node in tree at the same position as node_to_match,
             or node in tree isn't a leaf node.
        """
        other_pixel, other_tree = self._get_tree_and_pixel_from_node(node_to_match)
        if other_pixel not in self:
            raise ValueError("No node in tree matching given node")
        if self[other_pixel] != PixelNodeType.LEAF:
            raise ValueError("Node in tree is not a leaf node")
        pixels_to_add = other_tree.get_child_pixels(other_pixel)
        while len(pixels_to_add) > 0:
            pixel = pixels_to_add.pop(0)
            pixels_to_add += other_tree.get_child_pixels(pixel)
            parent_pixel = (pixel[0] - 1, get_lower_order_pixel(pixel[0], pixel[1], 1))
            parent_node_type = self[parent_pixel]
            if parent_node_type == PixelNodeType.LEAF:
                self.pixels[parent_pixel[0]][parent_pixel[1]] = PixelNodeType.INNER
                for child_pixel in get_higher_order_pixels(parent_pixel[0], parent_pixel[1], delta_order=1):
                    self.create_node((parent_pixel[0] + 1, child_pixel), PixelNodeType.LEAF)
