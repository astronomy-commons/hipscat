from hipscat.pixel_tree.pixel_alignment import align_trees
from hipscat.pixel_tree.pixel_tree import PixelTree


def assert_trees_equal(tree1: PixelTree, tree2: PixelTree):
    assert len(tree1.pixels) == len(tree2.pixels)
    for order, nodes_at_order in tree1.pixels.items():
        assert order in tree2.pixels
        assert len(tree2.pixels[order]) == len(nodes_at_order)
        for pixel, node in nodes_at_order.items():
            assert (order, pixel) in tree2
            tree2_node = tree2[(order, pixel)]
            assert node.node_type == tree2_node.node_type


def test_pixel_tree_alignment_same_tree(pixel_tree_1):
    alignment = align_trees(pixel_tree_1, pixel_tree_1, "inner")
    assert_trees_equal(pixel_tree_1, alignment.pixel_tree)


def test_pixel_tree_alignment_inner(pixel_tree_2, pixel_tree_3, aligned_trees_2_3_inner):
    alignment = align_trees(pixel_tree_2, pixel_tree_3, "inner")
    assert_trees_equal(alignment.pixel_tree, aligned_trees_2_3_inner)


def test_pixel_tree_alignment_left(pixel_tree_2, pixel_tree_3, aligned_trees_2_3_left):
    alignment = align_trees(pixel_tree_2, pixel_tree_3, "left")
    assert_trees_equal(alignment.pixel_tree, aligned_trees_2_3_left)


def test_pixel_tree_alignment_right(pixel_tree_2, pixel_tree_3, aligned_trees_2_3_right):
    alignment = align_trees(pixel_tree_2, pixel_tree_3, "right")
    assert_trees_equal(alignment.pixel_tree, aligned_trees_2_3_right)


def test_pixel_tree_alignment_outer(pixel_tree_2, pixel_tree_3, aligned_trees_2_3_outer):
    alignment = align_trees(pixel_tree_2, pixel_tree_3, "outer")
    assert_trees_equal(alignment.pixel_tree, aligned_trees_2_3_outer)
