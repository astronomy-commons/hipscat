"""Tests of partition info functionality"""

import os

from hipscat.catalog import PartitionInfo
from hipscat.pixel_math import HealpixPixel


def test_load_partition_info_small_sky(small_sky_dir):
    """Instantiate the partition info for catalog with 1 pixel"""
    partitions = PartitionInfo(small_sky_dir)

    partition_file_list = partitions.get_file_names()
    assert len(partition_file_list) == 1

    for parquet_file in partition_file_list:
        assert os.path.exists(parquet_file)

    order_pixel_pairs = partitions.get_healpix_pixels()
    assert len(order_pixel_pairs) == 1
    expected = [HealpixPixel(0, 11)]
    assert order_pixel_pairs == expected


def test_load_partition_info_small_sky_order1(small_sky_order1_dir):
    """Instantiate the partition info for catalog with 4 pixels"""
    partitions = PartitionInfo(small_sky_order1_dir)

    partition_file_list = partitions.get_file_names()
    assert len(partition_file_list) == 4

    for parquet_file in partition_file_list:
        assert os.path.exists(parquet_file)

    order_pixel_pairs = partitions.get_healpix_pixels()
    assert len(order_pixel_pairs) == 4
    expected = [
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]
    assert order_pixel_pairs == expected
