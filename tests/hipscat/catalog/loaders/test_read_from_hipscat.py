import pytest

from hipscat.catalog import CatalogType
from hipscat.loaders import read_from_hipscat


def test_read_from_hipscat_wrong_catalog_type(small_sky_dir):
    with pytest.raises(ValueError, match="must have type"):
        read_from_hipscat(small_sky_dir, catalog_type=CatalogType.ASSOCIATION)
    with pytest.raises(NotImplementedError, match="load catalog of type"):
        read_from_hipscat(small_sky_dir, catalog_type="unknown")
