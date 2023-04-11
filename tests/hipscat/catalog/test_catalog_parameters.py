"""Tests of catalog creation properties"""

import os

import pytest

import hipscat.io.write_metadata as io
from hipscat.catalog.catalog_parameters import (CatalogParameters,
                                                read_from_metadata_file)


def test_create_catalog_params(tmp_path):
    """Test that we can create catalog parameters with good values"""
    args = CatalogParameters(
        catalog_name="catalog",
        output_path=tmp_path,
    )

    ## We didn't specify the catalog path - make sure it exists
    assert args.catalog_path

    formatted_string = str(args)
    assert "catalog" in formatted_string
    assert str(tmp_path) in formatted_string


def test_bad_catalog_params(tmp_path):
    """Test that we can't create parameters with bad values"""

    with pytest.raises(ValueError):
        CatalogParameters(
            catalog_name="catalog",
            catalog_type="unknown",
            output_path=tmp_path,
        )


def test_read_from_metadata_file(tmp_path):
    """Test basic reading from metadata file."""
    basic_catalog_info = CatalogParameters(
        catalog_name="catalog",
        output_path=tmp_path,
    )

    io.write_catalog_info(basic_catalog_info)
    metadata_filename = os.path.join(tmp_path, "catalog", "catalog_info.json")

    read_catalog_info = read_from_metadata_file(metadata_filename)
    assert basic_catalog_info.catalog_name == read_catalog_info.catalog_name
    assert basic_catalog_info.catalog_type == read_catalog_info.catalog_type
    assert basic_catalog_info.epoch == read_catalog_info.epoch
    assert basic_catalog_info.ra_column == read_catalog_info.ra_column
    assert basic_catalog_info.dec_column == read_catalog_info.dec_column
    assert basic_catalog_info.total_rows == read_catalog_info.total_rows


def test_bad_file_contents(tmp_path):
    """Test parsing the catalog info file with bad file contents."""

    catalog_path = os.path.join(tmp_path, "empty")
    os.makedirs(catalog_path, exist_ok=True)

    file_name = os.path.join(catalog_path, "catalog_info.json")

    ## Malformed json
    with pytest.raises(ValueError):
        with open(
            file_name,
            "w",
            encoding="utf-8",
        ) as metadata_file:
            metadata_file.write('{catalog_name:"empty"}')

        read_from_metadata_file(file_name)

    ## Empty catalog name
    with pytest.raises(ValueError):
        with open(
            file_name,
            "w",
            encoding="utf-8",
        ) as metadata_file:
            metadata_file.write('{"catalog_name":""}')

        read_from_metadata_file(file_name)

    ## Bad catalog type
    with pytest.raises(ValueError):
        with open(
            file_name,
            "w",
            encoding="utf-8",
        ) as metadata_file:
            metadata_file.write('{"catalog_name":"empty", "catalog_type": "empty"}')

        read_from_metadata_file(file_name)

    ## Non-integer total_rows
    with pytest.raises(ValueError):
        with open(
            file_name,
            "w",
            encoding="utf-8",
        ) as metadata_file:
            metadata_file.write('{"catalog_name":"empty", "total_rows":"empty"}')

        read_from_metadata_file(file_name)
