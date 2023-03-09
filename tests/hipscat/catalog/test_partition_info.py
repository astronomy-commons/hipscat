"""Tests of catalog functionality"""

import os

from hipscat.catalog import PartitionInfo


def test_load_catalog_small_sky(small_sky_dir):
    """Instantiate a catalog with 1 pixel"""
    partitions = PartitionInfo(small_sky_dir)

    partition_file_list = partitions.get_file_names()
    assert len(partition_file_list) == 1

    for parquet_file in partition_file_list:
        assert os.path.exists(parquet_file)


def test_load_catalog_small_sky_order1(small_sky_order1_dir):
    """Instantiate a catalog with 4 pixels"""
    partitions = PartitionInfo(small_sky_order1_dir)

    partition_file_list = partitions.get_file_names()
    assert len(partition_file_list) == 4

    for parquet_file in partition_file_list:
        assert os.path.exists(parquet_file)
