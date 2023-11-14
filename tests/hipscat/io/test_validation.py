"""Test catalog information is valid"""
import os

from hipscat.catalog import PartitionInfo
from hipscat.io import get_file_pointer_from_path, paths, write_catalog_info
from hipscat.io.validation import is_valid_catalog


def test_is_valid_catalog(tmp_path, small_sky_catalog, small_sky_pixels):
    """Tests if the catalog_info and partition_info files are valid"""
    # An empty directory means an invalid catalog
    catalog_dir_pointer = get_file_pointer_from_path(tmp_path)
    assert not is_valid_catalog(catalog_dir_pointer)

    # Having the catalog_info file is not enough
    write_catalog_info(catalog_dir_pointer, small_sky_catalog.catalog_info)
    assert not is_valid_catalog(catalog_dir_pointer)

    # The catalog is valid if both the catalog_info and _metadata files exist,
    # and the catalog_info is in a valid format
    partition_info_pointer = paths.get_parquet_metadata_pointer(catalog_dir_pointer)
    PartitionInfo.from_healpix(small_sky_pixels).write_to_metadata_files(catalog_dir_pointer)
    assert is_valid_catalog(catalog_dir_pointer)

    # A partition_info file alone is also not enough
    catalog_info_pointer = paths.get_catalog_info_pointer(catalog_dir_pointer)
    os.remove(catalog_info_pointer)
    assert not is_valid_catalog(catalog_dir_pointer)

    # The catalog_info file needs to be in the correct format
    small_sky_catalog.catalog_info.catalog_type = "invalid"
    write_catalog_info(catalog_dir_pointer, small_sky_catalog.catalog_info)
    assert not is_valid_catalog(catalog_dir_pointer)
