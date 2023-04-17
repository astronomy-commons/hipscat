from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree


def test_pixel_tree_length():
    lengths = [1, 3, 6]
    for length in lengths:
        root_node = PixelNode((-1, -1), PixelNodeType.ROOT, None)
        last_node = root_node
        nodes = {-1: {-1: root_node}}
        for order in range(length):
            last_node = PixelNode((order, 0), PixelNodeType.INNER, last_node)
            nodes[order] = {0: last_node}
        tree = PixelTree(root_pixel=root_node, pixels=nodes)
        assert len(tree) == length + 1


def test_pixel_tree_contains():
    root_node = PixelNode((-1, -1), PixelNodeType.ROOT, None)
    leaf_node = PixelNode((0, 0), PixelNodeType.LEAF, root_node)
    nodes = {-1: {-1: root_node}, 0: {0: leaf_node}}
    tree = PixelTree(root_pixel=root_node, pixels=nodes)
    assert tree.contains((0, 0))
    assert tree.contains(HealpixPixel(0, 0))
    assert (0, 0) in tree
    assert HealpixPixel(0, 0) in tree
    assert not tree.contains((1, 1))
    assert not tree.contains(HealpixPixel(1, 1))
    assert (1, 1) not in tree
    assert HealpixPixel(1, 1) not in tree


def test_pixel_tree_get_node():
    root_node = PixelNode((-1, -1), PixelNodeType.ROOT, None)
    leaf_node = PixelNode((0, 0), PixelNodeType.LEAF, root_node)
    nodes = {-1: {-1: root_node}, 0: {0: leaf_node}}
    tree = PixelTree(root_pixel=root_node, pixels=nodes)
    assert tree.get_node((0, 0)) == leaf_node
    assert tree.get_node(HealpixPixel(0, 0)) == leaf_node
    assert tree[(0, 0)] == leaf_node
    assert tree[HealpixPixel(0, 0)] == leaf_node
    assert tree.get_node((1, 1)) is None
    assert tree.get_node(HealpixPixel(1, 1)) is None
    assert tree[(1, 1)] is None
    assert tree[HealpixPixel(1, 1)] is None
