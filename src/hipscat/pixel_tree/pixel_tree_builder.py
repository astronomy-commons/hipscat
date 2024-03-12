# pylint: disable=duplicate-code

from __future__ import annotations

from typing import List, Tuple

import numpy as np

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
        result = np.vstack((starts, ends)).T
        result.sort(axis=0)
        return PixelTree(result, max_order)
