import pytest

from hipscat.catalog import CatalogType
from hipscat.loaders import read_from_hipscat


def test_read_from_hipscat_wrong_catalog_type(small_sky_dir):
    with pytest.raises(ValueError, match="must have type"):
        read_from_hipscat(small_sky_dir, catalog_type=CatalogType.ASSOCIATION)
    with pytest.raises(NotImplementedError, match="load catalog of type"):
        read_from_hipscat(small_sky_dir, catalog_type="unknown")


def test_read_hipscat_branches(
    small_sky_dir,
    small_sky_order1_dir,
    association_catalog_path,
    small_sky_source_object_index_dir,
    margin_catalog_path,
    small_sky_source_dir,
):
    read_from_hipscat(small_sky_dir)
    read_from_hipscat(small_sky_order1_dir)
    read_from_hipscat(association_catalog_path)
    read_from_hipscat(small_sky_source_object_index_dir)
    read_from_hipscat(margin_catalog_path)
    read_from_hipscat(small_sky_source_dir)
