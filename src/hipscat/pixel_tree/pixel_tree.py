from __future__ import annotations

from hipscat.pixel_math import HealpixInputTypes, get_healpix_pixel
from hipscat.pixel_tree.pixel_node import PixelNode


class PixelTree:
    """Sparse Quadtree of HEALPix pixels that make up the HiPSCat catalog

    This class stores each node in the tree, with leaf nodes corresponding to pixels with data
    files.

    There are a number of methods in this class which allow for quickly navigating through the
    tree and performing operations to filter the pixels in the catalog.

    Attributes:
        pixels: Nested dictionary of pixel nodes stored in the tree. Indexed by HEALPix
            order then pixel number
        root_pixel: Root node of the tree. Its children are a subset of the
            12 base HEALPix pixels
    """

    def __init__(self, root_pixel: PixelNode, pixels: dict[int, dict[int, PixelNode]]) -> None:
        """Initialises a tree object from the nodes in the tree

        Args:
            root_pixel: PixelNode representing the root node in the tree
            pixels: Dictionary containing all PixelNodes in the tree
        """
        self.root_pixel = root_pixel
        self.pixels = pixels

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
        pixel = get_healpix_pixel(pixel)
        return pixel.order in self.pixels and pixel.pixel in self.pixels[pixel.order]

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
            return self.pixels[pixel.order][pixel.pixel]
        return None

    def __getitem__(self, item):
        return self.get_node(item)
