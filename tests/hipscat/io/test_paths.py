"""Test pixel path creation"""

import pytest

import hipscat.io.paths as paths


def test_pixel_directory():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder0/Npix5"
    result = paths.pixel_directory("/foo", 0, 5)
    assert result == expected


def test_pixel_directory_nonint():
    """Simple case with non-integer inputs"""
    with pytest.raises(ValueError):
        paths.pixel_directory("/foo", "zero", "five")


def test_pixel_catalog_file():
    """Simple case with sensical inputs"""
    expected = "/foo/Norder0/Npix5/catalog.parquet"
    result = paths.pixel_catalog_file("/foo", 0, 5)
    assert result == expected


def test_pixel_catalog_file_nonint():
    """Simple case with non-integer inputs"""
    with pytest.raises(ValueError):
        paths.pixel_catalog_file("/foo", "zero", "five")
