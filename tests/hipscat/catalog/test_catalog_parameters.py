"""Tests of catalog creation properties"""

import pytest

from hipscat.catalog.catalog_parameters import CatalogParameters


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
