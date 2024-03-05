from __future__ import annotations

from typing import List, Tuple

import healpy as hp
import numpy as np

from hipscat.pixel_math import HealpixInputTypes, HealpixPixel, get_healpix_pixel
from hipscat.pixel_math.healpix_pixel import get_lower_order_pixel, get_higher_order_pixels
from hipscat.pixel_math.healpix_pixel_convertor import get_healpix_tuple
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType


class PixelTree:
    """Sparse Quadtree of HEALPix pixels that make up the HiPSCat catalog

    This class stores each node in the tree, with leaf nodes corresponding to pixels with data
    files.

    There are a number of methods in this class which allow for quickly navigating through the
    tree and performing operations to filter the pixels in the catalog.

    Attributes:
        pixels: Nested dictionary of pixel nodes stored in the tree. Indexed by HEALPix
            order then pixel number
    """

    def __init__(self, pixels: dict[int, dict[int, PixelNodeType]]) -> None:
        """Initialises a tree object from the nodes in the tree

        Args:
            pixels: Dictionary containing all PixelNodes in the tree
        """
        self.pixels = pixels

    @property
    def root_pixel(self):
        return self[(-1, -1)]

    def __len__(self):
        """Gets the number of nodes in the tree, including inner nodes and the root node

        Returns:
            The number of nodes in the tree, including inner nodes and the root node
        """
        pixel_count = 0
        for _, order_pixels in self.pixels.items():
            pixel_count += len(order_pixels)
        return pixel_count

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

    def get_node(self, pixel: HealpixInputTypes) -> PixelNode | None:
        """Get the node at a given pixel

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)

        Returns:
            The PixelNode at the index, or None if a node does not exist
        """
        pixel = get_healpix_pixel(pixel)
        if self.contains(pixel):
            return PixelNode(pixel, self.pixels[pixel.order][pixel.pixel], self)
        return None

    def __getitem__(self, item):
        return self.get_node(item)

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

    def get_max_depth(self) -> int:
        """Get the max depth (or highest healpix order) represented in the list of pixels.

        Returns:
            max depth (or highest healpix order) of the pixels in the tree
        """
        return max(self.pixels.keys())

    def get_parent_node_type(self, pixel: HealpixInputTypes) -> PixelNodeType:
        (order, pixel) = get_healpix_tuple(pixel)
        parent_order = order - 1
        parent_pixel = get_lower_order_pixel(order, pixel, 1) if parent_order != 0 else -1
        return self.get_node_type((parent_order, parent_pixel))

    def get_parent_node(self, pixel: HealpixInputTypes) -> PixelNode:
        pixel = get_healpix_pixel(pixel)
        parent_pixel = pixel.convert_to_lower_order(1) if pixel.order != 0 else HealpixPixel(-1, -1)
        return self[parent_pixel]

    def get_child_pixels(self, pixel: HealpixInputTypes) -> List[Tuple[int, int]]:
        (order, pixel) = get_healpix_tuple(pixel)
        child_order = order + 1
        child_pixels = get_higher_order_pixels(order, pixel, 1)
        children_in_tree = [self.contains((child_order, p)) for p in child_pixels]
        child_pixels_in_tree = [(child_order, p) for p in child_pixels[children_in_tree]]
        return child_pixels_in_tree

    def get_child_nodes(self, pixel: HealpixInputTypes) -> List[PixelNode]:
        pixel = get_healpix_pixel(pixel)
        child_pixels = pixel.convert_to_higher_order(1)
        child_nodes = [self[p] for p in child_pixels if p in self]
        return child_nodes

    def get_leaf_nodes_at_healpix_pixel(self, pixel: HealpixInputTypes) -> List[PixelNode]:
        """Lookup all leaf nodes that contain or are within a given HEALPix pixel

        - Exact matches will return a list with only the matching pixel
        - A pixel that is within a lower order pixel in the tree will return a list with the lower
          order pixel
        - A pixel that has higher order pixels within found in the tree will return a list with all
          higher order pixels
        - A pixel with no matching leaf nodes in the tree will return an empty list

        Args:
            pixel: HEALPix pixel of the pixel to lookup

        Returns:
            A list of the leaf PixelNodes in the tree that align with the specified pixel
        """
        pixel = get_healpix_pixel(pixel)

        if self.contains(pixel):
            # Pixel exists in tree. Either a leaf node with an exact match for the search pixel,
            # or an inner node, so the search pixel will contain leaf nodes at higher orders
            node_in_tree = self.get_node(pixel)
            return node_in_tree.get_all_leaf_descendants()
        # if the pixel doesn't exist in the tree, it's either because the tree doesn't cover the
        # pixel, or the pixel is at a higher order than the tree at that location, so we search for
        # lower order nodes in the tree
        node_in_tree = self._find_first_lower_order_leaf_node_in_tree(pixel)
        if node_in_tree is None:
            return []
        return [node_in_tree]

    def _find_first_lower_order_leaf_node_in_tree(self, pixel: HealpixInputTypes) -> PixelNode | None:
        pixel = get_healpix_pixel(pixel)
        for delta_order in range(1, pixel.order + 1):
            lower_pixel = pixel.convert_to_lower_order(delta_order)
            if self.contains(lower_pixel):
                lower_node = self.get_node(lower_pixel)
                if lower_node.node_type == PixelNodeType.LEAF:
                    # If the catalog doesn't fully cover the sky, it's possible we encounter an
                    # inner node whose leaf children don't cover the search pixel.
                    return lower_node
                return None
        return None

    def get_leaf_pixels_at_healpix_pixel(self, pixel: HealpixInputTypes) -> List[Tuple[int, int]]:
        pixel = get_healpix_tuple(pixel)
        if pixel in self:
            return self.get_leaf_descendent_pixels(pixel)

        pixel_in_tree = self._find_first_lower_order_leaf_pixel_in_tree(pixel)
        if pixel_in_tree is None:
            return []
        return [pixel_in_tree]

    def get_leaf_descendent_pixels(self, pixel: HealpixInputTypes) -> List[Tuple[int, int]]:
        order, pixel = get_healpix_tuple(pixel)
        leaf_descendants = []
        self._add_all_leaf_descendants_rec(order, pixel, leaf_descendants)
        return leaf_descendants

    def _add_all_leaf_descendants_rec(self, order: int, pixel: int, leaf_descendants: List[Tuple[int, int]]):
        """Recursively add all leaf descendants to list

        list must be created outside function, done for efficiency vs list concat
        """
        if self.get_node_type((order, pixel)) == PixelNodeType.LEAF:
            leaf_descendants.append((order, pixel))

        for child_order, child_pixel in self.get_child_pixels((order, pixel)):
            # pylint: disable=protected-access
            self._add_all_leaf_descendants_rec(child_order, child_pixel, leaf_descendants)

    def _find_first_lower_order_leaf_pixel_in_tree(self, pixel: HealpixInputTypes) -> Tuple[int, int] | None:
        order, pixel = get_healpix_tuple(pixel)
        for delta_order in range(1, order + 1):
            lower_pixel = get_lower_order_pixel(order, pixel, delta_order)
            lower_order = order - delta_order
            if self.contains((lower_order, lower_pixel)):
                lower_node_type = self.get_node_type((lower_order, lower_pixel))
                if lower_node_type == PixelNodeType.LEAF:
                    # If the catalog doesn't fully cover the sky, it's possible we encounter an
                    # inner node whose leaf children don't cover the search pixel.
                    return (lower_order, lower_pixel)
                return None
        return None

    # pylint: disable=too-many-locals
    def get_negative_pixels(self) -> List[HealpixPixel]:
        """Get the leaf nodes at each healpix order that have zero catalog data.

        For example, if an example catalog only had data points in pixel 0 at
        order 0, then this method would return order 0's pixels 1 through 11.
        Used for getting full coverage on margin caches.

        Returns:
            List of HealpixPixels representing the 'negative tree' for the catalog.
        """
        max_depth = self.get_max_depth()
        missing_pixels = []
        pixels_at_order = self.root_pixel.children

        covered_orders = []
        for order_i in range(0, max_depth + 1):
            npix = hp.nside2npix(2**order_i)
            covered_orders.append(np.zeros(npix))

        for order in range(0, max_depth + 1):
            next_order_children = []
            leaf_pixels = []

            for node in pixels_at_order:
                pixel = node.pixel.pixel
                covered_orders[order][pixel] = 1
                if node.node_type == PixelNodeType.LEAF:
                    leaf_pixels.append(pixel)
                else:
                    next_order_children.extend(node.children)

            zero_leafs = np.argwhere(covered_orders[order] == 0).flatten()
            for pix in zero_leafs:
                missing_pixels.append(HealpixPixel(order, pix))
                leaf_pixels.append(pix)

            pixels_at_order = next_order_children

            for order_j in range(order + 1, max_depth + 1):
                explosion_factor = 4 ** (order_j - order)
                for pixel in leaf_pixels:
                    covered_pix = range(pixel * explosion_factor, (pixel + 1) * explosion_factor)
                    covered_orders[order_j][covered_pix] = 1

        return missing_pixels
