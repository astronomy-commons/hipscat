import numpy.testing as npt

from hipscat.catalog.index.index_catalog import IndexCatalog
from hipscat.loaders import read_from_hipscat
from hipscat.pixel_math import HealpixPixel


def test_loc_partition(small_sky_source_object_index_dir):
    catalog = read_from_hipscat(small_sky_source_object_index_dir)

    assert isinstance(catalog, IndexCatalog)
    assert catalog.on_disk
    assert catalog.catalog_path == str(small_sky_source_object_index_dir)

    npt.assert_array_equal(catalog.loc_partitions([700]), [HealpixPixel(2, 184)])
    npt.assert_array_equal(catalog.loc_partitions([707]), [HealpixPixel(2, 176), HealpixPixel(2, 178)])
    npt.assert_array_equal(catalog.loc_partitions([900]), [])
