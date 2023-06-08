from hipscat.inspection.almanac import Almanac
from hipscat.inspection.almanac_catalog_info import AlmanacCatalogInfo


def test_from_catalog_dir(small_sky_dir):
    """Load from a directory."""
    almanac_info = AlmanacCatalogInfo.from_catalog_dir(small_sky_dir)
    assert almanac_info.catalog_name == "small_sky"


def test_write_to_file(tmp_path, small_sky_dir):
    """Write out the almanac to file and make sure we can read it again."""
    almanac_info = AlmanacCatalogInfo.from_catalog_dir(small_sky_dir)
    assert almanac_info.catalog_name == "small_sky"

    almanac_info.write_to_file(tmp_path, default_dir=False)

    alms = Almanac(include_default_dir=False, dirs=tmp_path)
    assert len(alms.catalogs()) == 1
