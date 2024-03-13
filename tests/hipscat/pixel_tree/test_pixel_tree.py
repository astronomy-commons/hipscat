from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def test_pixel_tree_length():
    lengths = [1, 3, 6]
    orders = [1, 2, 7]
    for order in orders:
        for length in lengths:
            hp_pixels = [(order, i) for i in range(length)]
            tree = PixelTreeBuilder.from_healpix(hp_pixels)
            assert len(tree) == length


def test_pixel_tree_max_depth(pixel_tree_1, pixel_tree_2, pixel_tree_3):
    assert pixel_tree_1.get_max_depth() == 0
    assert pixel_tree_2.get_max_depth() == 2
    assert pixel_tree_3.get_max_depth() == 1


def test_pixel_tree_contains():
    tree = PixelTreeBuilder.from_healpix([(0, 0)])
    assert tree.contains((0, 0))
    assert tree.contains(HealpixPixel(0, 0))
    assert (0, 0) in tree
    assert HealpixPixel(0, 0) in tree
    assert not tree.contains((1, 1))
    assert not tree.contains(HealpixPixel(1, 1))
    assert (1, 1) not in tree
    assert HealpixPixel(1, 1) not in tree
