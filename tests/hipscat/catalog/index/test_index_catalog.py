import os

import numpy.testing as npt

from hipscat.loaders import read_from_hipscat
from hipscat.pixel_math import HealpixPixel


def test_loc_partition(test_data_dir):
    index_catalog_dir = os.path.join(test_data_dir, "small_sky_source_object_index")
    catalog = read_from_hipscat(index_catalog_dir)

    assert catalog.on_disk
    assert catalog.catalog_path == index_catalog_dir

    npt.assert_array_equal(catalog.loc_partitions([700]), [HealpixPixel(2, 184)])
    npt.assert_array_equal(catalog.loc_partitions([707]), [HealpixPixel(2, 176), HealpixPixel(2, 178)])
    npt.assert_array_equal(catalog.loc_partitions([900]), [])
