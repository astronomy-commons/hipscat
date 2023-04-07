"""Test pixel path creation"""

import pytest

from hipscat.io import paths


def test_pixel_directory():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder=0/Dir=0"
    result = paths.pixel_directory("/foo", 0, 5)
    assert result == expected


def test_pixel_directory_number():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder=0/Dir=0"
    result = paths.pixel_directory(
        "/foo", pixel_order=0, pixel_number=5, directory_number=0
    )
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
