from __future__ import annotations

import pandas as pd

from hipscat.catalog import PixelNode, PixelNodeType


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
