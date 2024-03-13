from __future__ import annotations

from typing import List, Tuple

import healpy as hp
import numpy as np

from hipscat.pixel_math import HealpixInputTypes, HealpixPixel
from hipscat.pixel_math.healpix_pixel_convertor import get_healpix_tuple
from hipscat.pixel_math.healpix_pixel_function import get_pixels_from_intervals
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

    def __init__(self, pixels: np.ndarray, order: int) -> None:
        """Initialises a tree object from the nodes in the tree

        Args:
            pixels: Dictionary containing all PixelNodes in the tree
        """
        self.tree_order = order
        self.tree = pixels
        # store transpose and orders for efficient searches
        self._tree_t = pixels.T

        if not np.all((self._tree_t[0, 1:] - self._tree_t[1, :-1]) >= 0):
            raise ValueError("Invalid Catalog: Tree contains overlapping pixels")

        self.pixels = get_pixels_from_intervals(self._tree_t, self.tree_order).T

    def __len__(self):
        """Gets the number of nodes in the tree

        Returns:
            The number of nodes in the tree
        """
        return len(self.tree)

    def contains(self, pixel: HealpixInputTypes) -> bool:
        """Check if tree contains a node at a given order and pixel

        Args:
            pixel: HEALPix pixel to check. Either of type `HealpixPixel`
                or a tuple of (order, pixel)

        Returns:
            True if the tree contains the pixel, False if not
        """
        (order, pixel) = get_healpix_tuple(pixel)
        if order > self.tree_order:
            return False
        d_order = self.tree_order - order
        pixel_at_tree_order = pixel << 2 * d_order
        index = np.searchsorted(self._tree_t[1], pixel_at_tree_order, side='right')
        is_same_order = self.pixels[index][0] == order
        return pixel_at_tree_order == self.tree[index][0] and is_same_order

    def __contains__(self, item):
        return self.contains(item)

    def get_max_depth(self) -> int:
        """Get the max depth (or highest healpix order) represented in the list of pixels.

        Returns:
            max depth (or highest healpix order) of the pixels in the tree
        """
        return self.tree_order

    def get_healpix_pixels(self) -> List[HealpixPixel]:
        return np.vectorize(HealpixPixel)(self.pixels.T[0], self.pixels.T[1])

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
