import os

import pytest

from hipscat.catalog import PartitionInfo
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


@pytest.fixture
def pixel_trees_dir(test_data_dir):
    return os.path.join(test_data_dir, "pixel_trees")


@pytest.fixture
def pixel_tree_1():
    return PixelTreeBuilder.from_healpix([HealpixPixel(0, 11)])


@pytest.fixture
def pixel_tree_2():
    return PixelTreeBuilder.from_healpix(
        [
            HealpixPixel(0, 10),
            HealpixPixel(1, 33),
            HealpixPixel(1, 35),
            HealpixPixel(1, 44),
            HealpixPixel(1, 45),
            HealpixPixel(1, 46),
            HealpixPixel(2, 128),
            HealpixPixel(2, 130),
            HealpixPixel(2, 131),
        ]
    )


@pytest.fixture
def pixel_tree_3():
    return PixelTreeBuilder.from_healpix(
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
def aligned_trees_2_3_inner_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "aligned_2_3_inner.csv")


@pytest.fixture
def aligned_trees_2_3_left_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "aligned_2_3_left.csv")


@pytest.fixture
def aligned_trees_2_3_right_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "aligned_2_3_right.csv")


@pytest.fixture
def aligned_trees_2_3_outer_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "aligned_2_3_outer.csv")


@pytest.fixture
def aligned_trees_2_3_inner(aligned_trees_2_3_inner_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_inner_path)
    return PixelTreeBuilder.from_healpix(partition_info.get_healpix_pixels())


@pytest.fixture
def aligned_trees_2_3_left(aligned_trees_2_3_left_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_left_path)
    return PixelTreeBuilder.from_healpix(partition_info.get_healpix_pixels())


@pytest.fixture
def aligned_trees_2_3_right(aligned_trees_2_3_right_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_right_path)
    return PixelTreeBuilder.from_healpix(partition_info.get_healpix_pixels())


@pytest.fixture
def aligned_trees_2_3_outer(aligned_trees_2_3_outer_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_outer_path)
    return PixelTreeBuilder.from_healpix(partition_info.get_healpix_pixels())
