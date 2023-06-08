

import pytest

from hipscat.inspection.almanac_catalog_info import AlmanacCatalogInfo


def test_from_catalog_dir(small_sky_dir):
    """Load from a directory."""
    almanac_info = AlmanacCatalogInfo.from_catalog_dir(small_sky_dir)
    assert almanac_info.catalog_name == "small_sky"