from __future__ import annotations

from typing import List

from hipscat.pixel_math import HealpixInputTypes, get_healpix_pixel
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
