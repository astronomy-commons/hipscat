from hipscat.pixel_tree.pixel_alignment import PixelAlignment
from hipscat.pixel_tree.pixel_alignment_types import PixelAlignmentType
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def test_pixel_tree_alignment():
    left_tree_builder = PixelTreeBuilder()
    left_tree_builder.create_node((0, 0), PixelNodeType.INNER)
    left_tree_builder.create_node((0, 1), PixelNodeType.LEAF)
    left_tree_builder.create_node((1, 0), PixelNodeType.LEAF)
    right_tree_builder = PixelTreeBuilder()
    right_tree_builder.create_node((0, 0), PixelNodeType.LEAF)
    right_tree_builder.create_node((0, 1), PixelNodeType.INNER)
    right_tree_builder.create_node((1, 4), PixelNodeType.LEAF)
    left_tree = left_tree_builder.build()
    right_tree = right_tree_builder.build()
    aligned_tree = PixelAlignment.align_trees(left_tree, right_tree, alignment_type=PixelAlignmentType.OUTER)
    print(aligned_tree.pixels)
