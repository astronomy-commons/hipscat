# pylint: disable=duplicate-code

from __future__ import annotations

from typing import List

from hipscat.pixel_math.healpix_pixel_convertor import HealpixInputTypes
from hipscat.pixel_tree.pixel_tree import PixelTree


class PixelTreeBuilder:
    """Build a PixelTree

    Initially a root node is created when the builder is initialized.
    Nodes can then be added to the tree.
    To create a pixel tree object once the tree is built, call the `build` method

    """

    @staticmethod
    def from_healpix(healpix_pixels: List[HealpixInputTypes]) -> PixelTree:
        """Build a tree from a list of constituent healpix pixels

        Args:
            healpix_pixels: list of healpix pixels

        Returns:
            The pixel tree with the leaf pixels specified in the list
        """
        return PixelTree.from_healpix(healpix_pixels)
