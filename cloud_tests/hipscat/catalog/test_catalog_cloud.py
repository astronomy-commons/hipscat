"""Tests of catalog functionality"""

import os

import pytest

from hipscat.catalog import Catalog, PartitionInfo
from hipscat.io.file_io import file_io


def test_load_catalog_small_sky(small_sky_dir_cloud, example_cloud_storage_options):
    """Instantiate a catalog with 1 pixel"""
    cat = Catalog.read_from_hipscat(small_sky_dir_cloud, storage_options=example_cloud_storage_options)

    assert cat.catalog_name == "small_sky"
    assert len(cat.get_healpix_pixels()) == 1


def test_load_catalog_small_sky_order1(small_sky_order1_dir_cloud, example_cloud_storage_options):
    """Instantiate a catalog with 4 pixels"""
    cat = Catalog.read_from_hipscat(small_sky_order1_dir_cloud, storage_options=example_cloud_storage_options)

    assert cat.catalog_name == "small_sky_order1"
    assert len(cat.get_healpix_pixels()) == 4


def test_cone_filter(small_sky_order1_catalog_cloud):
    filtered_catalog = small_sky_order1_catalog_cloud.filter_by_cone(315, -66.443, 0.1)
    assert len(filtered_catalog.partition_info.data_frame) == 1
    assert filtered_catalog.partition_info.data_frame[PartitionInfo.METADATA_PIXEL_COLUMN_NAME][0] == 44
    assert filtered_catalog.partition_info.data_frame[PartitionInfo.METADATA_ORDER_COLUMN_NAME][0] == 1
    assert (1, 44) in filtered_catalog.pixel_tree
    assert len(filtered_catalog.pixel_tree.pixels[1]) == 1
    assert filtered_catalog.catalog_info.total_rows is None


def test_cone_filter_big(small_sky_order1_catalog_cloud):
    filtered_catalog = small_sky_order1_catalog_cloud.filter_by_cone(315, -66.443, 30)
    assert len(filtered_catalog.partition_info.data_frame) == 4
    assert (1, 44) in filtered_catalog.pixel_tree
    assert (1, 45) in filtered_catalog.pixel_tree
    assert (1, 46) in filtered_catalog.pixel_tree
    assert (1, 47) in filtered_catalog.pixel_tree


def test_cone_filter_empty(small_sky_order1_catalog_cloud):
    filtered_catalog = small_sky_order1_catalog_cloud.filter_by_cone(0, 0, 0.1)
    assert len(filtered_catalog.partition_info.data_frame) == 0
    assert len(filtered_catalog.pixel_tree) == 1


def test_empty_directory(tmp_dir_cloud, example_cloud_storage_options):
    """Test loading empty or incomplete data"""
    catalog_path = os.path.join(tmp_dir_cloud, "empty")

    ## Path exists but there's nothing there
    with pytest.raises(FileNotFoundError):
        Catalog.read_from_hipscat(catalog_path, storage_options=example_cloud_storage_options)

    ## catalog_info file exists - getting closer
    file_name = os.path.join(catalog_path, "catalog_info.json")
    file_io.write_string_to_file(
        file_name,
        string='{"catalog_name":"empty", "catalog_type":"source"}',
        storage_options=example_cloud_storage_options,
    )

    with pytest.raises(FileNotFoundError):
        Catalog.read_from_hipscat(catalog_path, storage_options=example_cloud_storage_options)

    ## partition_info file exists - enough to create a catalog
    file_name = os.path.join(catalog_path, "partition_info.csv")
    file_io.write_string_to_file(file_name, string="foo", storage_options=example_cloud_storage_options)

    catalog = Catalog.read_from_hipscat(catalog_path, storage_options=example_cloud_storage_options)
    assert catalog.catalog_name == "empty"

    file_io.delete_file(
        os.path.join(catalog_path, "catalog_info.json"), storage_options=example_cloud_storage_options
    )
    file_io.delete_file(
        os.path.join(catalog_path, "partition_info.csv"), storage_options=example_cloud_storage_options
    )
