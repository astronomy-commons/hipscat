"""Two sample benchmarks to compute runtime and memory usage.

For more information on writing benchmarks:
https://asv.readthedocs.io/en/stable/writing_benchmarks.html."""

import os

import healpy as hp
import numpy as np

import hipscat.pixel_math as hist
from hipscat.catalog import Catalog, PartitionInfo
from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree import PixelAlignment, align_trees
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
    pixels = [HealpixPixel(6, 30), HealpixPixel(7, 124), HealpixPixel(7, 5000)]
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


class MetadataSuite:
    """Suite that generates catalog files and benchmarks the operations on them."""

    def setup_cache(self):
        root_dir = os.getcwd()

        ## Create partition info for catalog a (only at order 7)
        pixel_list_a = [HealpixPixel(7, pixel) for pixel in np.arange(100_000)]
        catalog_path_a = os.path.join(root_dir, "catalog_a")
        os.makedirs(catalog_path_a, exist_ok=True)
        partition_info = PartitionInfo.from_healpix(pixel_list_a)
        partition_info.write_to_file(os.path.join(catalog_path_a, "partition_info.csv"))

        ## Create partition info for catalog a (only at order 6)
        pixel_list_b = [HealpixPixel(6, pixel) for pixel in np.arange(25_000)]
        catalog_path_b = os.path.join(root_dir, "catalog_b")
        os.makedirs(catalog_path_b, exist_ok=True)
        partition_info = PartitionInfo.from_healpix(pixel_list_b)
        partition_info.write_to_file(os.path.join(catalog_path_b, "partition_info.csv"))

        ## Fake an association table between the two
        tree_a = PixelTreeBuilder.from_healpix(pixel_list_a)
        tree_b = PixelTreeBuilder.from_healpix(pixel_list_b)
        alignment = align_trees(tree_a, tree_b)
        alignment_df = alignment.pixel_mapping[
            [
                PixelAlignment.PRIMARY_ORDER_COLUMN_NAME,
                PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME,
                PixelAlignment.JOIN_ORDER_COLUMN_NAME,
                PixelAlignment.JOIN_PIXEL_COLUMN_NAME,
            ]
        ]
        alignment_df = alignment_df.rename(
            columns={
                PixelAlignment.PRIMARY_ORDER_COLUMN_NAME: "Norder",
                PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME: "Npix",
            }
        )

        association_catalog_path = os.path.join(root_dir, "assocation_a_b")
        os.makedirs(association_catalog_path, exist_ok=True)
        partition_info = PartitionJoinInfo(alignment_df)
        partition_info.write_to_csv(association_catalog_path)

        return (catalog_path_a, catalog_path_b, association_catalog_path)

    def time_load_partition_info_order7(self, cache):
        PartitionInfo.read_from_dir(cache[0])

    def time_load_partition_info_order6(self, cache):
        PartitionInfo.read_from_dir(cache[1])

    def time_load_partition_join_info(self, cache):
        PartitionInfo.read_from_dir(cache[2])
