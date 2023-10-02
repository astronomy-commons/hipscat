"""Test pixel path creation"""
import tempfile

import pytest

from hipscat.catalog import PartitionInfo
from hipscat.io import paths, get_file_pointer_from_path, write_catalog_info, write_partition_info
from hipscat.io.paths import is_valid_catalog


def test_pixel_directory():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder=0/Dir=0"
    result = paths.pixel_directory("/foo", 0, 5)
    assert result == expected


def test_pixel_directory_number():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder=0/Dir=0"
    result = paths.pixel_directory("/foo", pixel_order=0, pixel_number=5, directory_number=0)
    assert result == expected

    result = paths.pixel_directory("/foo", pixel_order=0, directory_number=0)
    assert result == expected


def test_pixel_directory_missing():
    """Simple case with missing inputs"""
    with pytest.raises(ValueError):
        paths.pixel_directory("/foo", 0)


def test_pixel_directory_nonint():
    """Simple case with non-integer inputs"""
    with pytest.raises(ValueError):
        paths.pixel_directory("/foo", "zero", "five")


def test_pixel_catalog_file():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder=0/Dir=0/Npix=5.parquet"
    result = paths.pixel_catalog_file("/foo", 0, 5)
    assert result == expected


def test_pixel_catalog_file_nonint():
    """Simple case with non-integer inputs"""
    with pytest.raises(ValueError):
        paths.pixel_catalog_file("/foo", "zero", "five")


def test_pixel_association_file():
    """Simple case with non-integer inputs"""
    result = paths.pixel_association_file("/foo", 0, 5, 0, 4)
    expected = "/foo/Norder=0/Dir=0/Npix=5/join_Norder=0/join_Dir=0/join_Npix=4.parquet"
    assert result == expected


def test_pixel_association_file_nonint():
    """Simple case with non-integer inputs"""
    with pytest.raises(ValueError):
        paths.pixel_association_file("/foo", "zero", "five", "zero", "four")


def test_pixel_association_directory():
    """Simple case with non-integer inputs"""
    result = paths.pixel_association_directory("/foo", 0, 5, 0, 4)
    expected = "/foo/Norder=0/Dir=0/Npix=5/join_Norder=0/join_Dir=0"
    assert result == expected


def test_pixel_association_directory_nonint():
    """Simple case with non-integer inputs"""
    with pytest.raises(ValueError):
        paths.pixel_association_directory("/foo", "zero", "five", "zero", "four")


def test_is_valid_catalog(tmp_path, small_sky_catalog, small_sky_pixels):
    """Tests existence of the catalog_info and partition_info files"""
    catalog_dir_fp = get_file_pointer_from_path(tmp_path)
    assert not is_valid_catalog(catalog_dir_fp)
    write_catalog_info(catalog_dir_fp, small_sky_catalog.catalog_info)
    PartitionInfo.from_healpix(small_sky_pixels).write_to_file(catalog_dir_fp)
    assert is_valid_catalog(catalog_dir_fp)
