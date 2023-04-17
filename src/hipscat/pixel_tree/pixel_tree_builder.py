import pandas as pd

from hipscat.catalog import PartitionInfo
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
        self.root_pixel = PixelNode(-1, -1, PixelNodeType.ROOT, None)
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
        builder._create_tree_from_partition_info_df(partition_info_df)  # pylint: disable=W0212
        return builder.build()

    def contains(self, hp_order: int, hp_pixel: int) -> bool:
        """Check if tree contains a node at a given order and pixel

        Args:
            hp_order: HEALPix order to check
            hp_pixel: HEALPix pixel number to check

        Returns:
            True if the tree contains the pixel, False if not
        """
        return hp_order in self.pixels and hp_pixel in self.pixels[hp_order]

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
                row[PartitionInfo.METADATA_ORDER_COLUMN_NAME],
                row[PartitionInfo.METADATA_PIXEL_COLUMN_NAME],
                PixelNodeType.LEAF,
            )

    def create_node_and_parent_if_not_exist(
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
            self.create_node(hp_order, hp_pixel, node_type, self.root_pixel)
            return

        parent_order = hp_order - 1
        parent_pixel = hp_pixel >> 2
        if not self.contains(parent_order, parent_pixel):
            self.create_node_and_parent_if_not_exist(
                parent_order, parent_pixel, PixelNodeType.INNER
            )

        parent = self.pixels[parent_order][parent_pixel]

        if parent.node_type != PixelNodeType.INNER:
            raise ValueError(
                "Incorrectly configured catalog: catalog contains pixels defined at "
                "multiple orders"
            )

        self.create_node(hp_order, hp_pixel, node_type, parent)

    def create_node(
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
