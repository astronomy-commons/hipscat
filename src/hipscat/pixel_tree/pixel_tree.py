from __future__ import annotations

from hipscat.pixel_tree.pixel_node import PixelNode


class PixelTree:
    """Sparse Quadtree of HEALPix pixels that make up the HiPSCat catalog

    This class stores each node in the tree, with leaf nodes corresponding to pixels with data
    files.

    There are a number of methods in this class which allow for quickly navigating through the
    tree and performing operations to filter the pixels in the catalog.

    Attributes:
        pixels: Nested dictionary of pixel nodes stored in the tree. Indexed by HEALPix
        order then pixel number root_pixel: Root node of the tree. Its children are a subset of the
        12 base HEALPix pixels
    """

    def __init__(self, root_pixel: PixelNode, pixels: dict[int, dict[int, PixelNode]]) -> None:
        """Initialises a tree object from the nodes in the tree

        Args:
            root_pixel: PixelNode representing the root node in the tree
            pixels: Dictionary containing all PixelNodes in the tree

        Raises:
            ValueError: Incorrectly configured pixel structure in metadata file
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

    def contains(self, hp_order: int, hp_pixel: int) -> bool:
        """Check if tree contains a node at a given order and pixel

        Args:
            hp_order: HEALPix order to check
            hp_pixel: HEALPix pixel number to check

        Returns:
            True if the tree contains the pixel, False if not
        """
        return hp_order in self.pixels and hp_pixel in self.pixels[hp_order]

    def get_node(self, hp_order: int, hp_pixel: int) -> PixelNode | None:
        """Get the node at a given order and pixel

        Args:
            hp_order: HEALPix order to get
            hp_pixel: HEALPix pixel number to get

        Returns:
            The PixelNode at the index, or None if a node does not exist
        """
        if self.contains(hp_order, hp_pixel):
            return self.pixels[hp_order][hp_pixel]
        return None
