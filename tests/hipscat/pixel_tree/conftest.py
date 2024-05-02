import os

import pytest

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_tree import PixelTree


@pytest.fixture
def pixel_trees_dir(test_data_dir):
    return os.path.join(test_data_dir, "pixel_trees")


@pytest.fixture
def pixel_tree_1():
    return PixelTree.from_healpix([HealpixPixel(0, 11)])


@pytest.fixture
def pixel_tree_2_pixels():
    return [
            HealpixPixel(2, 128),
            HealpixPixel(2, 130),
            HealpixPixel(2, 131),
            HealpixPixel(1, 33),
            HealpixPixel(1, 35),
            HealpixPixel(0, 10),
            HealpixPixel(1, 44),
            HealpixPixel(1, 45),
            HealpixPixel(1, 46),
        ]


@pytest.fixture
def pixel_tree_2(pixel_tree_2_pixels):
    return PixelTree.from_healpix(
        pixel_tree_2_pixels
    )


@pytest.fixture
def pixel_tree_3():
    return PixelTree.from_healpix(
        [
            HealpixPixel(0, 8),
            HealpixPixel(1, 36),
            HealpixPixel(1, 37),
            HealpixPixel(1, 40),
            HealpixPixel(1, 42),
            HealpixPixel(1, 43),
            HealpixPixel(1, 44),
            HealpixPixel(1, 46),
            HealpixPixel(1, 47),
        ]
    )


@pytest.fixture
def aligned_trees_2_3_inner():
    return PixelTree.from_healpix(
        [
            HealpixPixel(1, 33),
            HealpixPixel(1, 35),
            HealpixPixel(1, 40),
            HealpixPixel(1, 42),
            HealpixPixel(1, 43),
            HealpixPixel(1, 44),
            HealpixPixel(1, 46),
            HealpixPixel(2, 128),
            HealpixPixel(2, 130),
            HealpixPixel(2, 131),
        ]
    )


@pytest.fixture
def aligned_trees_2_3_left():
    return PixelTree.from_healpix(
        [
            HealpixPixel(1, 33),
            HealpixPixel(1, 35),
            HealpixPixel(1, 40),
            HealpixPixel(1, 41),
            HealpixPixel(1, 42),
            HealpixPixel(1, 43),
            HealpixPixel(1, 44),
            HealpixPixel(1, 45),
            HealpixPixel(1, 46),
            HealpixPixel(2, 128),
            HealpixPixel(2, 130),
            HealpixPixel(2, 131),
        ]
    )


@pytest.fixture
def aligned_trees_2_3_right():
    return PixelTree.from_healpix(
        [
            HealpixPixel(1, 33),
            HealpixPixel(1, 34),
            HealpixPixel(1, 35),
            HealpixPixel(1, 36),
            HealpixPixel(1, 37),
            HealpixPixel(1, 40),
            HealpixPixel(1, 42),
            HealpixPixel(1, 43),
            HealpixPixel(1, 44),
            HealpixPixel(1, 46),
            HealpixPixel(1, 47),
            HealpixPixel(2, 128),
            HealpixPixel(2, 129),
            HealpixPixel(2, 130),
            HealpixPixel(2, 131),
        ]
    )


@pytest.fixture
def aligned_trees_2_3_outer():
    return PixelTree.from_healpix(
        [
            HealpixPixel(1, 33),
            HealpixPixel(1, 34),
            HealpixPixel(1, 35),
            HealpixPixel(1, 36),
            HealpixPixel(1, 37),
            HealpixPixel(1, 40),
            HealpixPixel(1, 41),
            HealpixPixel(1, 42),
            HealpixPixel(1, 43),
            HealpixPixel(1, 44),
            HealpixPixel(1, 45),
            HealpixPixel(1, 46),
            HealpixPixel(1, 47),
            HealpixPixel(2, 128),
            HealpixPixel(2, 129),
            HealpixPixel(2, 130),
            HealpixPixel(2, 131),
        ]
    )
