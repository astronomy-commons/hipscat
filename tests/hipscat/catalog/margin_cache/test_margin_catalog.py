import json
import os

import pytest

from hipscat.catalog import CatalogType, MarginCatalog, PartitionInfo
from hipscat.loaders import read_from_hipscat


def test_init_catalog(margin_catalog_info, margin_catalog_pixels):
    catalog = MarginCatalog(margin_catalog_info, margin_catalog_pixels)
    assert catalog.catalog_name == margin_catalog_info.catalog_name
    assert catalog.get_healpix_pixels() == margin_catalog_pixels
    assert catalog.catalog_info == margin_catalog_info

    assert len(catalog.get_healpix_pixels()) == len(margin_catalog_pixels)
    for hp_pixel in catalog.get_healpix_pixels():
        assert hp_pixel in margin_catalog_pixels
        assert hp_pixel in catalog.pixel_tree


def test_wrong_catalog_type(margin_catalog_info, margin_catalog_pixels):
    margin_catalog_info.catalog_type = CatalogType.OBJECT
    with pytest.raises(ValueError, match="catalog_type"):
        MarginCatalog(margin_catalog_info, margin_catalog_pixels)


def test_wrong_catalog_info_type(catalog_info, margin_catalog_pixels):
    catalog_info.catalog_type = CatalogType.MARGIN
    with pytest.raises(TypeError, match="catalog_info"):
        MarginCatalog(catalog_info, margin_catalog_pixels)


def test_read_from_file(margin_catalog_path, margin_catalog_pixels):
    catalog = read_from_hipscat(margin_catalog_path)

    assert isinstance(catalog, MarginCatalog)
    assert catalog.on_disk
    assert catalog.catalog_path == margin_catalog_path
    assert len(catalog.get_healpix_pixels()) == len(margin_catalog_pixels)
    assert catalog.get_healpix_pixels() == margin_catalog_pixels

    info = catalog.catalog_info
    assert info.catalog_name == "small_sky_order1_margin"
    assert info.catalog_type == CatalogType.MARGIN
    assert info.primary_catalog == "small_sky_order1"
    assert info.margin_threshold == 7200


# pylint: disable=duplicate-code
def test_empty_directory(tmp_path, margin_cache_catalog_info_data, margin_catalog_pixels):
    """Test loading empty or incomplete data"""
    ## Path doesn't exist
    with pytest.raises(FileNotFoundError):
        read_from_hipscat(os.path.join("path", "empty"))

    catalog_path = os.path.join(tmp_path, "empty")
    os.makedirs(catalog_path, exist_ok=True)

    ## Path exists but there's nothing there
    with pytest.raises(FileNotFoundError, match="catalog_info"):
        read_from_hipscat(catalog_path)

    ## catalog_info file exists - getting closer
    file_name = os.path.join(catalog_path, "catalog_info.json")
    with open(file_name, "w", encoding="utf-8") as metadata_file:
        metadata_file.write(json.dumps(margin_cache_catalog_info_data))

    with pytest.raises(FileNotFoundError, match="metadata"):
        read_from_hipscat(catalog_path)

    ## Now we create the needed _metadata and everything is right.
    part_info = PartitionInfo.from_healpix(margin_catalog_pixels)
    part_info.write_to_metadata_files(catalog_path=catalog_path)

    with pytest.warns(UserWarning, match="slow"):
        catalog = read_from_hipscat(catalog_path)
    assert catalog.catalog_name == margin_cache_catalog_info_data["catalog_name"]
