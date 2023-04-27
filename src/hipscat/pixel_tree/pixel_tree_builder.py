# pylint: disable=duplicate-code

from __future__ import annotations

import pandas as pd

from hipscat.catalog.partition_info import PartitionInfo
from hipscat.pixel_math.healpix_pixel_convertor import (HealpixInputTypes,
                                                        get_healpix_pixel)
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

    def __getitem__(self, item) -> PixelNode:
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
            self,
            pixel: HealpixInputTypes,
            node_type: PixelNodeType,
            parent: PixelNode = None,
            split_leaf_parent=False,
            replace_existing_node=False,
    ):
        """Create a node and add to `self.pixels` in the tree

        Args:
            pixel: HEALPix pixel to get. Either of type `HealpixPixel`
                or a tuple of (order, pixel)
            node_type: Node type of the node to create
            parent: (Default: None) Parent node of the node to create. If None, will get parent from
                existing node in tree at correct position based on pixel
            split_leaf_parent: (Default: False) If True and parent is of node type leaf, the parent
                node in the tree will be changed to an inner node and leaf nodes for all child
                pixels will be created.
            replace_existing_node: (Default: False) If True and node at `pixel` already exists,
                the existing node will be removed and replaced with the new node.
        """
        pixel = get_healpix_pixel(pixel)
        if parent is None:
            if pixel.order == 0:
                parent = self.root_pixel
            else:
                parent_pixel = pixel.convert_to_lower_order(delta_order=1)
                if parent_pixel not in self:
                    raise ValueError(
                        f"Cannot create node at {str(pixel)}, "
                        f"no parent node exists at {str(parent_pixel)}"
                    )
                parent = self[parent_pixel]
        if parent.node_type == PixelNodeType.LEAF:
            if not split_leaf_parent:
                raise ValueError(
                    f"Cannot create node at {str(pixel)}, "
                    f"parent node at {str(parent_pixel)} has node type leaf"
                )
            parent.node_type = PixelNodeType.INNER
            for child_pixel in parent.pixel.convert_to_higher_order(delta_order=1):
                if child_pixel != pixel:
                    self.create_node(child_pixel, PixelNodeType.LEAF, parent=parent)
        if pixel in self:
            if not replace_existing_node:
                raise ValueError(
                    f"Cannot create node at {str(pixel)}, node already exists"
                )
            node_to_delete = self[pixel]
            parent.remove_child_node(node_to_delete)
        node = PixelNode(pixel, node_type, parent)
        if pixel.order not in self.pixels:
            self.pixels[pixel.order] = {}
        self.pixels[pixel.order][pixel.pixel] = node

    def remove_node(self, pixel: HealpixInputTypes):
        pixel = get_healpix_pixel(pixel)
        if pixel not in self:
            raise ValueError(f"No node at pixel {str(pixel)}")
        node = self[pixel]
        node.parent.remove_child_node(node)
        self.pixels[pixel.order].pop(pixel.pixel)
        if len(self.pixels[pixel.order]) == 0:
            self.pixels.pop(pixel.order)

    def add_all_children_from_node(
            self,
            tree: PixelTree,
            pixel: HealpixInputTypes,
            split_leaf_parent=False,
            replace_existing_node=False
    ):
        pixel = get_healpix_pixel(pixel)
        nodes_to_add = tree[pixel].children
        while len(nodes_to_add) > 0:
            node = nodes_to_add.pop(0)
            nodes_to_add += node.children
            self.create_node(
                node.pixel,
                node.node_type,
                split_leaf_parent=split_leaf_parent,
                replace_existing_node=replace_existing_node
            )

    def remove_empty_inner_nodes(self):
        nodes_to_check = [child for child in self.root_pixel.children]
        for node in nodes_to_check:
            self._remove_node_if_no_leaf_children(node)

    def _remove_node_if_no_leaf_children(self, node: PixelNode) -> bool:
        if node.node_type == PixelNodeType.LEAF:
            return True
        if len(node.children) == 0:
            self.remove_node(node.pixel)
            return False
        has_leaf_children = False
        nodes_to_check = [child for child in node.children]
        for child in nodes_to_check:
            has_leaf_children = has_leaf_children or self._remove_node_if_no_leaf_children(child)
        if not has_leaf_children:
            self.remove_node(node.pixel)
        return has_leaf_children
