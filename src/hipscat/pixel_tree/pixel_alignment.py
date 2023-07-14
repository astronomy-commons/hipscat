from typing import List

import pandas as pd

from hipscat.pixel_math import HealpixInputTypes, HealpixPixel, get_healpix_pixel
from hipscat.pixel_tree.pixel_alignment_types import PixelAlignmentType
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


LEFT_TREE_KEY = "left"
RIGHT_TREE_KEY = "right"


# pylint: disable=R0903
class PixelAlignment:
    """Represents how two pixel trees align with each other, meaning which pixels match
    or overlap between the catalogs, and a new tree with the smallest pixels from each tree

    For more information on the pixel alignment algorithm, view this document:
    https://docs.google.com/document/d/1YFAQsGCgeEyEZ1IRIam9BbWdN5h2onV6ndO3VM-qjn0/edit?usp=sharing

    Attributes:
        pixel_mapping: A dataframe where each row contains a pixel from each tree that match, and
            which pixel in the aligned tree they match with
        pixel_tree: The aligned tree generated by using the smallest pixels in each tree. For
            example, a tree with pixels at order 0, pixel 1, and a tree with order 1, pixel 4,5,6,
            and 7, would result in the smaller order 1 pixels in the aligned tree.
        alignment_type: The type of alignment describing how to handle nodes which exist in one tree
            but not the other. Options are:
            inner - only use pixels that appear in both catalogs
            left - use all pixels that appear in the left catalog and any overlapping from the right
            right - use all pixels that appear in the right catalog and any overlapping from the
                left
            outer - use all pixels from both catalogs
    """

    PRIMARY_ORDER_COLUMN_NAME = "primary_Norder"
    PRIMARY_PIXEL_COLUMN_NAME = "primary_Npix"
    JOIN_ORDER_COLUMN_NAME = "join_Norder"
    JOIN_PIXEL_COLUMN_NAME = "join_Npix"
    ALIGNED_ORDER_COLUMN_NAME = "aligned_Norder"
    ALIGNED_PIXEL_COLUMN_NAME = "aligned_Npix"

    def __init__(
        self,
        aligned_tree: PixelTree,
        pixel_mapping: pd.DataFrame,
        alignment_type: PixelAlignmentType,
    ) -> None:
        self.pixel_tree = aligned_tree
        self.pixel_mapping = pixel_mapping
        self.alignment_type = alignment_type


# pylint: disable=R0912
def align_trees(
    left: PixelTree,
    right: PixelTree,
    alignment_type: PixelAlignmentType = PixelAlignmentType.INNER,
) -> PixelAlignment:
    """Generate a `PixelAlignment` object from two pixel trees

    A `PixelAlignment` represents how two pixel trees align with each other, meaning which pixels
    match or overlap between the catalogs, and includes a new tree with the smallest pixels from
    each tree

    For more information on the pixel alignment algorithm, view this document:
    https://docs.google.com/document/d/1YFAQsGCgeEyEZ1IRIam9BbWdN5h2onV6ndO3VM-qjn0/edit?usp=sharing

    Args:
        left: The left tree to align
        right: The right tree to align
        alignment_type: The type of alignment describing how to handle nodes which exist in one tree
            but not the other. Options are:
            inner - only use pixels that appear in both catalogs
            left - use all pixels that appear in the left catalog and any overlapping from the right
            right - use all pixels that appear in the right catalog and any overlapping from the
                left
            outer - use all pixels from both catalogs
    Returns:
        The `PixelAlignment` object with the alignment from the two trees
    """

    tree_builder = PixelTreeBuilder()
    pixels_to_search = _get_children_pixels_from_trees(
        [left, right], left.root_pixel.pixel
    )

    while len(pixels_to_search) > 0:
        search_pixel = pixels_to_search.pop(0)
        if search_pixel in left and search_pixel in right:
            left_node = left[search_pixel]
            right_node = right[search_pixel]
            if left_node.node_type == right_node.node_type:
                if left_node.node_type == PixelNodeType.LEAF:
                    # Matching leaf nodes get added to the aligned tree
                    tree_builder.create_node_and_parent_if_not_exist(
                        search_pixel, PixelNodeType.LEAF
                    )
                else:
                    # For matching inner nodes search into their children to check for alignment
                    pixels_to_search += _get_children_pixels_from_trees(
                        [left, right], search_pixel
                    )
            else:
                # Nodes with non-matching types: one must be a leaf and the other an inner node
                if left_node.node_type == PixelNodeType.LEAF:
                    tree_with_leaf_node = LEFT_TREE_KEY
                    inner_node = right_node
                else:
                    tree_with_leaf_node = RIGHT_TREE_KEY
                    inner_node = left_node
                if _should_include_all_pixels_from_tree(
                    tree_with_leaf_node, alignment_type
                ):
                    # If the alignment type means fully covering the tree with the leaf node, then
                    # create a leaf node in the aligned tree and split it to match the partitioning
                    # of the other tree to ensure the node is fully covered
                    tree_builder.create_node_and_parent_if_not_exist(
                        search_pixel, PixelNodeType.LEAF
                    )
                    tree_builder.split_leaf_to_match_partitioning(inner_node)
                else:
                    # Otherwise just add the subtree from the inner node to include all the
                    # overlapping pixels
                    tree_builder.create_node_and_parent_if_not_exist(
                        search_pixel, PixelNodeType.INNER
                    )
                    tree_builder.add_all_descendants_from_node(inner_node)
        elif search_pixel in left and search_pixel not in right:
            # For nodes that only exist in one tree, include them if the alignment type means that
            # tree should have all its nodes included
            if _should_include_all_pixels_from_tree(LEFT_TREE_KEY, alignment_type):
                tree_builder.create_node_and_parent_if_not_exist(
                    search_pixel, left[search_pixel].node_type
                )
                tree_builder.add_all_descendants_from_node(left[search_pixel])
        elif search_pixel in right and search_pixel not in left:
            if _should_include_all_pixels_from_tree(RIGHT_TREE_KEY, alignment_type):
                tree_builder.create_node_and_parent_if_not_exist(
                    search_pixel, right[search_pixel].node_type
                )
                tree_builder.add_all_descendants_from_node(right[search_pixel])
    tree = tree_builder.build()
    pixel_mapping = _generate_pixel_mapping_from_tree(left, right, tree)
    return PixelAlignment(tree, pixel_mapping, alignment_type)


def _get_children_pixels_from_trees(
    trees: List[PixelTree], pixel: HealpixInputTypes
) -> List[HealpixPixel]:
    """Returns the combined HEALPix pixels that have child nodes of the given pixel from trees

    This returns a list of HEALPix pixels, not the actual child nodes, and does not contain
    duplicate pixels if a pixel appears in multiple trees.

    Args:
        trees (List[PixelTree]): The list of trees to search for children from
        pixel (HealpixPixel | tuple[int,int]): The pixel to search for children at in all trees

    Returns:
        (List[HealpixPixel]) The list of all HEALPix pixels which have children of the given pixel
        in any of the trees.
    """
    pixel = get_healpix_pixel(pixel)
    pixels_to_add = set()
    for tree in trees:
        if pixel in tree:
            for node in tree[pixel].children:
                pixels_to_add.add(node.pixel)
    return list(pixels_to_add)


def _should_include_all_pixels_from_tree(
    tree_type: str, alignment_type: PixelAlignmentType
) -> bool:
    """If for a given alignment type, the left or right tree should include all pixels or just the
    ones that overlap with the other tree.

    Args:
        tree_type (str): 'left' for the left tree and 'right' for the right tree
        alignment_type (PixelAlignmentType): The type of alignment being performed

    Returns:
        A boolean indicating if the given tree type should include all pixels
    """
    left_add_types = [PixelAlignmentType.OUTER, PixelAlignmentType.LEFT]
    right_add_types = [PixelAlignmentType.OUTER, PixelAlignmentType.RIGHT]
    return (tree_type == LEFT_TREE_KEY and alignment_type in left_add_types) or \
        (tree_type == RIGHT_TREE_KEY and alignment_type in right_add_types)


def _generate_pixel_mapping_from_tree(
        left: PixelTree, right: PixelTree, aligned: PixelTree
) -> pd.DataFrame:
    """Generates a pixel mapping dataframe from two trees and their aligned tree

    The pixel mapping dataframe contains columns for the order and pixel of overlapping pixels in
    the left, right and aligned trees. The trees are searched through and this table is generated

    Args:
        left (PixelTree): the left tree used to generate the alignment
        right (PixelTree): the right tree used to generate the alignment
        aligned (PixelTree): the aligned tree as a result of aligning the left and right trees

    Returns:
        (pd.DataFrame) The pixel mapping dataframe where each row contains a pixel from the aligned
        tree and the pixels in the left and right tree that overlap with it
    """
    pixel_mapping_dict = {
        PixelAlignment.PRIMARY_ORDER_COLUMN_NAME: [],
        PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME: [],
        PixelAlignment.JOIN_ORDER_COLUMN_NAME: [],
        PixelAlignment.JOIN_PIXEL_COLUMN_NAME: [],
        PixelAlignment.ALIGNED_ORDER_COLUMN_NAME: [],
        PixelAlignment.ALIGNED_PIXEL_COLUMN_NAME: [],
    }
    for leaf_node in aligned.root_pixel.get_all_leaf_descendants():
        left_leaf_nodes = left.get_leaf_nodes_at_healpix_pixel(leaf_node.pixel)
        right_leaf_nodes = right.get_leaf_nodes_at_healpix_pixel(leaf_node.pixel)
        if len(left_leaf_nodes) == 0:
            left_leaf_nodes = [None]
        if len(right_leaf_nodes) == 0:
            right_leaf_nodes = [None]
        for left_node in left_leaf_nodes:
            for right_node in right_leaf_nodes:
                pixel_mapping_dict[PixelAlignment.ALIGNED_ORDER_COLUMN_NAME].append(
                    leaf_node.hp_order
                )
                pixel_mapping_dict[PixelAlignment.ALIGNED_PIXEL_COLUMN_NAME].append(
                    leaf_node.hp_pixel
                )
                left_order = left_node.hp_order if left_node is not None else None
                left_pixel = left_node.hp_pixel if left_node is not None else None
                pixel_mapping_dict[PixelAlignment.PRIMARY_ORDER_COLUMN_NAME].append(
                    left_order
                )
                pixel_mapping_dict[PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME].append(
                    left_pixel
                )
                right_order = right_node.hp_order if right_node is not None else None
                right_pixel = right_node.hp_pixel if right_node is not None else None
                pixel_mapping_dict[PixelAlignment.JOIN_ORDER_COLUMN_NAME].append(
                    right_order
                )
                pixel_mapping_dict[PixelAlignment.JOIN_PIXEL_COLUMN_NAME].append(
                    right_pixel
                )
    pixel_mapping = pd.DataFrame.from_dict(pixel_mapping_dict)
    return pixel_mapping
