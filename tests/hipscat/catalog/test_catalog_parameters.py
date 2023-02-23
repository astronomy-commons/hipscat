"""Tests of catalog creation properties"""

import tempfile

from hipscat.catalog.catalog_parameters import CatalogParameters


def test_create_catalog_info():
    """Test that we accurately write out catalog metadata"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = CatalogParameters(
            catalog_name="catalog",
            input_paths=["foo"],
            input_format="csv",
            output_path=tmp_dir,
            highest_healpix_order=0,
            ra_column="ra",
            dec_column="dec",
        )

        ## We didn't specify the catalog path - make sure it exists
        assert args.catalog_path

        formatted_string = str(args)
        assert "catalog" in formatted_string
        assert "csv" in formatted_string
        assert tmp_dir in formatted_string
