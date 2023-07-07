import os

import pytest

from hipscat.catalog import PartitionInfo
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


@pytest.fixture
def pixel_trees_dir(test_data_dir):
    return os.path.join(test_data_dir, "pixel_trees")


@pytest.fixture
def pixel_tree_1_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "pixel_tree_1.csv")


@pytest.fixture
def pixel_tree_2_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "pixel_tree_2.csv")


@pytest.fixture
def pixel_tree_3_path(pixel_trees_dir):
    return os.path.join(pixel_trees_dir, "pixel_tree_3.csv")


@pytest.fixture
def pixel_tree_1(pixel_tree_1_path):
    partition_info = PartitionInfo.read_from_file(pixel_tree_1_path)
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)


@pytest.fixture
def pixel_tree_2(pixel_tree_2_path):
    partition_info = PartitionInfo.read_from_file(pixel_tree_2_path)
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)


@pytest.fixture
def pixel_tree_3(pixel_tree_3_path):
    partition_info = PartitionInfo.read_from_file(pixel_tree_3_path)
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)


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
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)


@pytest.fixture
def aligned_trees_2_3_left(aligned_trees_2_3_left_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_left_path)
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)


@pytest.fixture
def aligned_trees_2_3_right(aligned_trees_2_3_right_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_right_path)
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)


@pytest.fixture
def aligned_trees_2_3_outer(aligned_trees_2_3_outer_path):
    partition_info = PartitionInfo.read_from_file(aligned_trees_2_3_outer_path)
    return PixelTreeBuilder.from_partition_info_df(partition_info.data_frame)
