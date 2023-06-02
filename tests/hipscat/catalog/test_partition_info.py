"""Tests of partition info functionality"""
import os

import pytest

from hipscat.catalog import PartitionInfo
from hipscat.io import file_io, paths
from hipscat.pixel_math import HealpixPixel


def test_load_partition_info_small_sky(small_sky_dir):
    """Instantiate the partition info for catalog with 1 pixel"""
    partition_info_file = paths.get_partition_info_pointer(small_sky_dir)
    partitions = PartitionInfo.read_from_file(partition_info_file)

    order_pixel_pairs = partitions.get_healpix_pixels()
    assert len(order_pixel_pairs) == 1
    expected = [HealpixPixel(0, 11)]
    assert order_pixel_pairs == expected


def test_load_partition_info_small_sky_order1(small_sky_order1_dir):
    """Instantiate the partition info for catalog with 4 pixels"""
    partition_info_file = paths.get_partition_info_pointer(small_sky_order1_dir)
    partitions = PartitionInfo.read_from_file(partition_info_file)

    order_pixel_pairs = partitions.get_healpix_pixels()
    assert len(order_pixel_pairs) == 4
    expected = [
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]
    assert order_pixel_pairs == expected


def test_load_partition_no_file(tmp_path):
    wrong_path = os.path.join(tmp_path, "wrong.csv")
    wrong_pointer = file_io.get_file_pointer_from_path(wrong_path)
    with pytest.raises(FileNotFoundError):
        PartitionInfo.read_from_file(wrong_pointer)


def test_get_highest_order(small_sky_order1_dir):
    """test the `get_highest_order` method"""
    partition_info_file = paths.get_partition_info_pointer(small_sky_order1_dir)
    partitions = PartitionInfo.read_from_file(partition_info_file)

    highest_order = partitions.get_highest_order()

    assert highest_order == 1
