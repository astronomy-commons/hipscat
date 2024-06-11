"""Test pixel path creation"""

import pytest

from hipscat.io import paths
from hipscat.pixel_math.healpix_pixel import INVALID_PIXEL, HealpixPixel


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


def test_pixel_catalog_files():
    expected = ["/foo/Norder=0/Dir=0/Npix=5.parquet", "/foo/Norder=1/Dir=0/Npix=16.parquet"]
    result = paths.pixel_catalog_files("/foo", [HealpixPixel(0, 5), HealpixPixel(1, 16)])
    assert expected == result


def test_pixel_catalog_files_w_query_params():
    expected = [
        "https://foo/Norder=0/Dir=0/Npix=5.parquet?columns=ID%2CRA%2CDEC%2Cr_auto&filters=r_auto%3C13"
    ]
    query_params = {"columns": ["ID", "RA", "DEC", "r_auto"], "filters": ["r_auto<13"]}
    result = paths.pixel_catalog_files("https://foo", [HealpixPixel(0, 5)], query_params=query_params)
    assert expected == result


def test_dict_to_query_urlparams():
    expected = "?columns=ID%2CRA%2CDEC%2Cr_auto&filters=r_auto%3C13"
    query_params = {"columns": ["ID", "RA", "DEC", "r_auto"], "filters": ["r_auto<13"]}
    result = paths.dict_to_query_urlparams(query_params)
    assert result == expected

    expected = "?columns=ID%2CRA%2CDEC%2Cr_auto&filters=r_auto%3C13"
    query_params = {"columns": [" ID", "RA ", "DEC ", "r_auto"], "filters": ["r_auto < 13"]}
    result = paths.dict_to_query_urlparams(query_params)
    assert result == expected

    result = paths.dict_to_query_urlparams({})
    assert result == ""


def test_get_healpix_from_path():
    expected = HealpixPixel(5, 34)

    # Test a few ways we could represent the path.
    result = paths.get_healpix_from_path("/foo/Norder=5/Dir=0/Npix=34.parquet")
    assert result == expected

    result = paths.get_healpix_from_path("Norder=5/Dir=0/Npix=34.pq")
    assert result == expected


def test_get_healpix_from_path_invalid():
    expected = INVALID_PIXEL

    # Test a few ways we could represent the path.
    result = paths.get_healpix_from_path("")
    assert result == expected

    result = paths.get_healpix_from_path("NORDER=5/Dir=0/PIXEL=34.pq")
    assert result == expected
