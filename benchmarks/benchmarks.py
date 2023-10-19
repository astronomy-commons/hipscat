"""Two sample benchmarks to compute runtime and memory usage.

For more information on writing benchmarks:
https://asv.readthedocs.io/en/stable/writing_benchmarks.html."""

import healpy as hp
import numpy as np

import hipscat.pixel_math as hist
from hipscat.catalog import Catalog
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def time_test_alignment_even_sky():
    """Create alignment from an even distribution at order 7"""
    initial_histogram = np.full(hp.order2npix(7), 40)
    result = hist.generate_alignment(initial_histogram, highest_order=7, threshold=1_000)
    # everything maps to order 5, given the density
    for mapping in result:
        assert mapping[0] == 5


def time_test_cone_filter_multiple_order():
    """Create a catalog cone filter where we have multiple orders in the catalog"""
    catalog_info = CatalogInfo(
        **{
            "catalog_name": "test_name",
            "catalog_type": "object",
            "total_rows": 10,
            "epoch": "J2000",
            "ra_column": "ra",
            "dec_column": "dec",
        }
    )
    pixels = [HealpixPixel(6, 30), HealpixPixel(7, 124), HealpixPixel(8, 5000)]
    catalog = Catalog(catalog_info, pixels)
    filtered_catalog = catalog.filter_by_cone(47.1, 6, 30)
    assert filtered_catalog.get_healpix_pixels() == [HealpixPixel(6, 30), HealpixPixel(7, 124)]


class Suite:
    def __init__(self) -> None:
        """Just initialize things"""
        self.pixel_list = None

    def setup(self):
        self.pixel_list = [HealpixPixel(8, pixel) for pixel in np.arange(100000)]

    def time_pixel_tree_creation(self):
        PixelTreeBuilder.from_healpix(self.pixel_list)
