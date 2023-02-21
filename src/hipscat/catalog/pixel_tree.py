from __future__ import annotations

from typing import List

import healpy as hp
import pandas as pd

from hipscat.catalog import PixelNode, PixelNodeType
from hipscat.pixel_math import calculate_lower_order_hp_pixel


class PixelTree:
    """Sparse Quadtree of HEALPix pixels that make up the HiPSCat catalog

    This class stores each node in the tree, with leaf nodes corresponding to pixels with data
    files.

    There are a number of methods in this class which allow for quickly navigating through the
    tree and performing operations to filter the pixels in the catalog.

    Attributes:
        pixels: Nested dictionary of pixel nodes stored in the tree. Indexed by HEALPix
        order then pixel number
        root_pixel: Root node of the tree. Its children are a subset of the  12 base HEALPix pixels
        max_order: The largest HEALPix order of the nodes stored in the tree
    """

    METADATA_ORDER_COLUMN_NAME = "order"
    METADATA_PIXEL_COLUMN_NAME = "pixel"

    def __init__(self, partition_info_df: pd.DataFrame):
        """Initialises the Tree from the partition info metadata

        Args:
            partition_info_df: Partition Info metadata file loaded into a pandas DataFrame

        Raises:
            ValueError: Incorrectly configured pixel structure in metadata file
        """
        self.root_pixel = PixelNode(-1, -1, PixelNodeType.ROOT, None)
        self.pixels = {-1: {-1: self.root_pixel}}
        self._create_tree(partition_info_df)
        self.max_order = max(hp_order for hp_order, _ in self.pixels.items())

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

    def _create_tree(self, partition_info_df: pd.DataFrame):
        """Creates the tree by recursively creating parent nodes until reaching the root from
        each leaf pixel

        Validates the pixel structure as it does so by checking for duplicate pixels or pixels
        defined at multiple orders

        Args:
            partition_info_df: Dataframe loaded from the partition_info metadata
        """
        for _, row in partition_info_df.iterrows():
            self._create_node_and_parent_if_not_exist(
                row[self.METADATA_ORDER_COLUMN_NAME],
                row[self.METADATA_PIXEL_COLUMN_NAME],
                PixelNodeType.LEAF,
            )

    def _create_node_and_parent_if_not_exist(
        self, hp_order: int, hp_pixel: int, node_type: PixelNodeType
    ):
        """Creates a node and adds to `self.pixels` in the tree, and recursively creates parent
        node if parent does not exist

        Args:
            hp_order: HEALPix order to create the node at
            hp_pixel: HEALPix pixel to create the node at
            node_type: Node type of the node to create
        """
        if self.contains(hp_order, hp_pixel):
            raise ValueError(
                "Incorrectly configured catalog: catalog contains duplicate pixels"
            )

        if hp_order == 0:
            self._create_node(hp_order, hp_pixel, node_type, self.root_pixel)
            return

        parent_order = hp_order - 1
        parent_pixel = hp_pixel >> 2
        if not self.contains(parent_order, parent_pixel):
            self._create_node_and_parent_if_not_exist(
                parent_order, parent_pixel, PixelNodeType.INNER
            )

        parent = self.pixels[parent_order][parent_pixel]

        if parent.node_type != PixelNodeType.INNER:
            raise ValueError(
                "Incorrectly configured catalog: catalog contains pixels defined at "
                "multiple orders"
            )

        self._create_node(hp_order, hp_pixel, node_type, parent)

    def _create_node(
        self, hp_order: int, hp_pixel: int, node_type: PixelNodeType, parent: PixelNode
    ):
        """Create a node and add to `self.pixels` in the tree

        Args:
            hp_order: HEALPix order to create the node at
            hp_pixel: HEALPix order to create the node at
            node_type: Node type of the node to create
            parent: Parent node of the node to create
        """
        node = PixelNode(hp_order, hp_pixel, node_type, parent)
        if hp_order not in self.pixels:
            self.pixels[hp_order] = {}
        self.pixels[hp_order][hp_pixel] = node

    def get_leaf_nodes_at_healpix_pixel(
        self, order: int, pixel: int
    ) -> List[PixelNode]:
        """Lookup all leaf nodes in this tree that match a given HEALPix pixel

        - Exact matches will return a list with only the matching pixel
        - A pixel that is within a lower order pixel in the tree will return a list with the lower
        order pixel
        - A pixel that has higher order pixels within found in the tree will return a list with all
        higher order pixels
        - A pixel with no matching leaf nodes in the tree will return an empty list

        Args:
            order: HEALPix order of the pixel to lookup
            pixel: HEALPix pixel number of the pixel to lookup, using nested scheme

        Returns:
            A list of the leaf PixelNodes in the tree that align with the specified pixel
        """

        if self.contains(order, pixel):
            node_in_tree = self.get_node(order, pixel)
            return node_in_tree.get_all_leaf_descendants()
        node_in_tree = self.find_first_lower_order_leaf_node_in_tree(order, pixel)
        if node_in_tree is None:
            return []
        return [node_in_tree]

    def find_first_lower_order_leaf_node_in_tree(
        self, order: int, pixel: int
    ) -> PixelNode | None:
        """Search for the highest order leaf node that contains a given pixel

        Args:
            order: HEALPix order of pixel to search
            pixel: HEALPix pixel number of pixel to search

        Returns:
            The PixelNode object of the found leaf node, or None if no leaf node is found
        """
        for delta_order in range(order + 1):
            lower_order, lower_pixel = calculate_lower_order_hp_pixel(
                order, pixel, delta_order
            )
            if self.contains(lower_order, lower_pixel):
                lower_node = self.get_node(lower_order, lower_pixel)
                if lower_node.node_type == PixelNodeType.LEAF:
                    return lower_node
                return None
        return None

    def get_leaf_node_containing_point(self, r_a: int, dec: int) -> PixelNode | None:
        """Lookup the leaf node that contains a point (ra, dec) in the tree

        If no leaf node with the point exists, returns None

        Args:
            r_a: Right Ascension of the point
            dec: Declination of the point

        Returns:
            The PixelNode object that contains the point, or None if no leaf node with the point
            exists
        """
        hp_nside = hp.order2nside(self.max_order)
        hp_pixel = hp.ang2pix(hp_nside, r_a, dec, lonlat=True, nest=True)
        matching_pixels = self.get_leaf_nodes_at_healpix_pixel(self.max_order, hp_pixel)
        if len(matching_pixels) > 0:
            return matching_pixels[0]
        return None
