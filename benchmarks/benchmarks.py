"""Two sample benchmarks to compute runtime and memory usage.

For more information on writing benchmarks:
https://asv.readthedocs.io/en/stable/writing_benchmarks.html."""

import healpy as hp
import numpy as np
import pandas as pd

import hipscat.pixel_math as hist
from hipscat.catalog import Catalog, PartitionInfo
from hipscat.catalog.catalog_info import CatalogInfo
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
    partition_info_df = pd.DataFrame.from_dict(
        {
            PartitionInfo.METADATA_ORDER_COLUMN_NAME: [6, 7, 7],
            PartitionInfo.METADATA_PIXEL_COLUMN_NAME: [30, 124, 5000],
        }
    )
    catalog = Catalog(catalog_info, partition_info_df)
    filtered_catalog = catalog.filter_by_cone(47.1, 6, 30)
    assert len(filtered_catalog.partition_info.data_frame) == 2
    assert (6, 30) in filtered_catalog.pixel_tree
    assert (7, 124) in filtered_catalog.pixel_tree


class Suite:
    def setup(self):
        self.partition_info_df = pd.DataFrame.from_dict(
            {
                PartitionInfo.METADATA_ORDER_COLUMN_NAME: np.full(100000, 8),
                PartitionInfo.METADATA_PIXEL_COLUMN_NAME: np.arange(100000),
            }
        )

    def time_pixel_tree_creation(self):
        PixelTreeBuilder.from_partition_info_df(self.partition_info_df)
