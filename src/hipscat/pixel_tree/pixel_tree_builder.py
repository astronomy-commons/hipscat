# pylint: disable=duplicate-code

from __future__ import annotations

import pandas as pd

from hipscat.catalog import PartitionInfo
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.util.healpix_pixel_convertor import (HealpixInputTypes,
                                                  get_healpix_pixel)


class PixelTreeBuilder:
    """Build a PixelTree

    Initially a root node is created when the builder is initialized.
    Nodes can then be added to the tree.
    To create a pixel tree object once the tree is built, call the `build` method

    """

    def __init__(self):
        self.root_pixel = PixelNode((-1, -1), PixelNodeType.ROOT, None)
        self.pixels = {-1: {-1: self.root_pixel}}

    def build(self) -> PixelTree:
        """Build a `PixelTree` object from the nodes created

        Returns:
            The pixel tree with the nodes created in the builder
        """
        return PixelTree(self.root_pixel, self.pixels)

    @staticmethod
    def from_partition_info_df(partition_info_df: pd.DataFrame) -> PixelTree:
        """Build a tree from a partition_info DataFrame

        Args:
            partition_info_df: Pandas Dataframe with columns matching those in the
            `partition_info.csv` metadata file

        Returns:
            The pixel tree with the leaf pixels specified in the DataFrame
        """
        builder = PixelTreeBuilder()
        # pylint: disable=protected-access
        builder._create_tree_from_partition_info_df(partition_info_df)
        return builder.build()

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

    def _create_tree_from_partition_info_df(self, partition_info_df: pd.DataFrame):
        """Creates the tree by recursively creating parent nodes until reaching the root from
        each leaf pixel

        Validates the pixel structure as it does so by checking for duplicate pixels or pixels
        defined at multiple orders

        Args:
            partition_info_df: Dataframe loaded from the partition_info metadata
        """
        for _, row in partition_info_df.iterrows():
            self.create_node_and_parent_if_not_exist(
                (
                    row[PartitionInfo.METADATA_ORDER_COLUMN_NAME],
                    row[PartitionInfo.METADATA_PIXEL_COLUMN_NAME],
                ),
                PixelNodeType.LEAF,
            )

    def create_node_and_parent_if_not_exist(
        self, pixel: HealpixInputTypes, node_type: PixelNodeType
    ):
        """Creates a node and adds to `self.pixels` in the tree, and recursively creates parent
        node if parent does not exist

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
        """
        pixel = get_healpix_pixel(pixel)
        if self.contains(pixel):
            raise ValueError(
                "Incorrectly configured catalog: catalog contains duplicate pixels"
            )

        if pixel.order == 0:
            self.create_node(pixel, node_type, self.root_pixel)
            return

        parent_order = pixel.order - 1
        parent_pixel = pixel.pixel >> 2
        if not self.contains((parent_order, parent_pixel)):
            self.create_node_and_parent_if_not_exist(
                (parent_order, parent_pixel), PixelNodeType.INNER
            )

        parent = self.pixels[parent_order][parent_pixel]

        if parent.node_type != PixelNodeType.INNER:
            raise ValueError(
                "Incorrectly configured catalog: catalog contains pixels defined at "
                "multiple orders"
            )

        self.create_node(pixel, node_type, parent)

    def create_node(
        self, pixel: HealpixInputTypes, node_type: PixelNodeType, parent: PixelNode
    ):
        """Create a node and add to `self.pixels` in the tree

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
            parent: Parent node of the node to create
        """
        pixel = get_healpix_pixel(pixel)
        node = PixelNode(pixel, node_type, parent)
        if pixel.order not in self.pixels:
            self.pixels[pixel.order] = {}
        self.pixels[pixel.order][pixel.pixel] = node
