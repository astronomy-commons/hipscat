"""Test catalog information is valid"""
import os

import pytest

from hipscat.catalog import PartitionInfo
from hipscat.io import get_file_pointer_from_path, paths, write_catalog_info
from hipscat.io.validation import is_valid_catalog


def test_is_valid_catalog(tmp_path, small_sky_catalog, small_sky_pixels):
    """Tests existence of the catalog_info and partition_info files"""
    # An empty directory means an invalid catalog
    catalog_dir_pointer = get_file_pointer_from_path(tmp_path)
    with pytest.raises(FileNotFoundError):
        assert not is_valid_catalog(catalog_dir_pointer)

    # Having the catalog_info file is not enough
    write_catalog_info(catalog_dir_pointer, small_sky_catalog.catalog_info)
    assert not is_valid_catalog(catalog_dir_pointer)

    # The catalog is valid if both catalog_info and partition_info files exist
    partition_info_pointer = paths.get_partition_info_pointer(catalog_dir_pointer)
    PartitionInfo.from_healpix(small_sky_pixels).write_to_file(partition_info_pointer)
    assert is_valid_catalog(catalog_dir_pointer)

    # A partition_info file is also not enough
    catalog_info_pointer = paths.get_catalog_info_pointer(catalog_dir_pointer)
    os.remove(catalog_info_pointer)
    with pytest.raises(FileNotFoundError):
        assert not is_valid_catalog(catalog_dir_pointer)
