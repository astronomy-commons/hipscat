from typing import List

import pandas as pd
from typing_extensions import Self

from hipscat.pixel_math import (HealpixInputTypes, HealpixPixel,
                                get_healpix_pixel)
from hipscat.pixel_tree.pixel_alignment_types import PixelAlignmentType
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


class PixelAlignment:

    PRIMARY_ORDER_COLUMN_NAME = "primary_Norder"
    PRIMARY_PIXEL_COLUMN_NAME = "primary_Npix"
    JOIN_ORDER_COLUMN_NAME = "join_Norder"
    JOIN_PIXEL_COLUMN_NAME = "join_Npix"
    ALIGNED_ORDER_COLUMN_NAME = "aligned_Norder"
    ALIGNED_PIXEL_COLUMN_NAME = "aligned_Npix"

    def __init__(self, aligned_tree: PixelTree, pixel_mapping: pd.DataFrame) -> None:
        self.pixel_tree = aligned_tree
        self.pixel_mapping = pixel_mapping


    @classmethod
    def align_trees(cls, left: PixelTree, right: PixelTree, alignment_type: PixelAlignmentType = PixelAlignmentType.INNER) -> Self:
        outer_trees = cls._get_outer_trees(left, right, alignment_type)
        tree_builder = PixelTreeBuilder()
        pixels_to_search = cls._get_children_pixels_from_trees([left, right],
                                                                left.root_pixel.pixel)

        while len(pixels_to_search) > 0:
            search_pixel = pixels_to_search.pop(0)
            if search_pixel in left and search_pixel in right:
                left_node = left[search_pixel]
                right_node = right[search_pixel]
                if left_node.node_type == right_node.node_type:
                    tree_builder.create_node(search_pixel, left_node.node_type)
                    pixels_to_search += cls._get_children_pixels_from_trees([left, right],
                                                                         search_pixel)
                else:
                    if left_node.node_type == PixelNodeType.LEAF:
                        if left in outer_trees:
                            tree_builder.create_node(search_pixel, PixelNodeType.LEAF)
                        else:
                            tree_builder.create_node(search_pixel, PixelNodeType.INNER)
                        tree_builder.add_all_children_from_node(right, search_pixel,
                                                                split_leaf_parent=True,
                                                                replace_existing_node=True)
                    else:
                        if right in outer_trees:
                            tree_builder.create_node(search_pixel, PixelNodeType.LEAF)
                        else:
                            tree_builder.create_node(search_pixel, PixelNodeType.INNER)
                        tree_builder.add_all_children_from_node(left, search_pixel,
                                                                split_leaf_parent=True,
                                                                replace_existing_node=True)
            elif search_pixel in left and search_pixel not in right:
                if left in outer_trees:
                    tree_builder.create_node(search_pixel, left[search_pixel].node_type)
                    tree_builder.add_all_children_from_node(left, search_pixel)
            elif search_pixel in right and search_pixel not in left:
                if right in outer_trees:
                    tree_builder.create_node(search_pixel, right[search_pixel].node_type)
                    tree_builder.add_all_children_from_node(right, search_pixel)
        tree_builder.remove_empty_inner_nodes()
        tree = tree_builder.build()
        pixel_mapping_dict = {
            cls.PRIMARY_ORDER_COLUMN_NAME: [],
            cls.PRIMARY_PIXEL_COLUMN_NAME: [],
            cls.JOIN_ORDER_COLUMN_NAME: [],
            cls.JOIN_PIXEL_COLUMN_NAME: [],
            cls.ALIGNED_ORDER_COLUMN_NAME: [],
            cls.ALIGNED_PIXEL_COLUMN_NAME: [],
        }
        for leaf_node in tree.root_pixel.get_all_leaf_descendants():
            left_leaf_nodes = left.get_leaf_nodes_at_healpix_pixel(leaf_node.pixel)
            right_leaf_nodes = right.get_leaf_nodes_at_healpix_pixel(leaf_node.pixel)
            if len(left_leaf_nodes) == 0:
                left_leaf_nodes = [None]
            if len(right_leaf_nodes) == 0:
                right_leaf_nodes = [None]
            for left_node in left_leaf_nodes:
                for right_node in right_leaf_nodes:
                    pixel_mapping_dict[cls.ALIGNED_ORDER_COLUMN_NAME].append(leaf_node.hp_order)
                    pixel_mapping_dict[cls.ALIGNED_PIXEL_COLUMN_NAME].append(leaf_node.hp_pixel)
                    left_order = left_node.hp_order if left_node is not None else None
                    left_pixel = left_node.hp_pixel if left_node is not None else None
                    pixel_mapping_dict[cls.PRIMARY_ORDER_COLUMN_NAME].append(left_order)
                    pixel_mapping_dict[cls.PRIMARY_PIXEL_COLUMN_NAME].append(left_pixel)
                    right_order = right_node.hp_order if right_node is not None else None
                    right_pixel = right_node.hp_pixel if right_node is not None else None
                    pixel_mapping_dict[cls.JOIN_ORDER_COLUMN_NAME].append(right_order)
                    pixel_mapping_dict[cls.JOIN_PIXEL_COLUMN_NAME].append(right_pixel)
        pixel_mapping = pd.DataFrame.from_dict(pixel_mapping_dict)
        return cls(tree, pixel_mapping)

    @staticmethod
    def _get_children_pixels_from_trees(trees: List[PixelTree], pixel: HealpixInputTypes) -> \
    List[HealpixPixel]:
        pixel = get_healpix_pixel(pixel)
        pixels_to_add = set()
        for tree in trees:
            if pixel in tree:
                for node in tree[pixel].children:
                    pixels_to_add.add(node.pixel)
        return list(pixels_to_add)

    @staticmethod
    def _get_outer_trees(left: PixelTree, right: PixelTree, alignment_type: PixelAlignmentType) -> \
    List[PixelTree]:
        trees = []
        left_add_types = [PixelAlignmentType.OUTER, PixelAlignmentType.LEFT]
        right_add_types = [PixelAlignmentType.OUTER, PixelAlignmentType.RIGHT]
        if alignment_type in left_add_types:
            trees.append(left)
        if alignment_type in right_add_types:
            trees.append(right)
        return trees
