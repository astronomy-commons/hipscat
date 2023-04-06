"""Tests of catalog functionality"""

import os

import pytest

from hipscat.catalog import Catalog


def test_load_catalog_small_sky(small_sky_dir):
    """Instantiate a catalog with 1 pixel"""
    cat = Catalog(small_sky_dir)

    assert cat.catalog_name == "small_sky"
    assert len(cat.get_pixels()) == 1


def test_load_catalog_small_sky_order1(small_sky_order1_dir):
    """Instantiate a catalog with 4 pixels"""
    cat = Catalog(small_sky_order1_dir)

    assert cat.catalog_name == "small_sky_order1"
    assert len(cat.get_pixels()) == 4


def test_empty_directory(tmp_path):
    """Test loading empty or incomplete data"""
    ## Path doesn't exist
    with pytest.raises(FileNotFoundError):
        Catalog(os.path.join("path", "empty"))

    catalog_path = os.path.join(tmp_path, "empty")
    os.makedirs(catalog_path, exist_ok=True)

    ## Path exists but there's nothing there
    with pytest.raises(FileNotFoundError):
        Catalog(catalog_path)

    ## catalog_info file exists - getting closer
    file_name = os.path.join(catalog_path, "catalog_info.json")
    with open(
        file_name,
        "w",
        encoding="utf-8",
    ) as metadata_file:
        metadata_file.write('{"catalog_name":"empty"}')

    with pytest.raises(FileNotFoundError):
        Catalog(catalog_path)

    ## partition_info file exists - enough to create a catalog
    file_name = os.path.join(catalog_path, "partition_info.csv")
    with open(
        file_name,
        "w",
        encoding="utf-8",
    ) as metadata_file:
        metadata_file.write("foo")

    catalog = Catalog(catalog_path)
    assert catalog.catalog_name == "empty"


def test_bad_file_contents(tmp_path):
    """Test parsing the catalog info file with bad file contents."""

    ## First, create necessary files and make sure we can load.
    catalog_path = os.path.join(tmp_path, "empty")
    os.makedirs(catalog_path, exist_ok=True)
    with open(
        os.path.join(catalog_path, "partition_info.csv"),
        "w",
        encoding="utf-8",
    ) as metadata_file:
        metadata_file.write("foo")

    file_name = os.path.join(catalog_path, "catalog_info.json")
    with open(
        file_name,
        "w",
        encoding="utf-8",
    ) as metadata_file:
        metadata_file.write('{"catalog_name":"empty"}')

    catalog = Catalog(catalog_path)
    assert catalog.catalog_name == "empty"

    ## Now, alter the catalog files and check for failures.
    file_name = os.path.join(catalog_path, "catalog_info.json")
    with open(
        file_name,
        "w",
        encoding="utf-8",
    ) as metadata_file:
        metadata_file.write('{"catalog_name":"empty", "catalog_type":"unknown"}')

    with pytest.raises(ValueError):
        Catalog(catalog_path)
