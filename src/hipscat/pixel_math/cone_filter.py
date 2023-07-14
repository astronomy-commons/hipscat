import healpy as hp
import numpy as np
import pandas as pd

from hipscat.catalog.partition_info import PartitionInfo
from hipscat.pixel_tree import PixelAlignment, PixelAlignmentType, align_trees
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_cone(pixel_tree: PixelTree, ra: float, dec: float, radius: float) -> PixelTree:
    """Filter the leaf pixels in a pixel tree to return a partition_info dataframe with the pixels
    that overlap with a cone

    Args:
        ra (float): Right Ascension of the center of the cone in degrees
        dec (float): Declination of the center of the cone in degrees
        radius (float): Radius of the cone in degrees

    Returns:
        A catalog_info dataframe with only the pixels that overlap with the specified cone
    """
    max_order = max(pixel_tree.pixels.keys())
    cone_tree = _generate_cone_pixel_tree(ra, dec, radius, max_order)
    cone_alignment = align_trees(pixel_tree, cone_tree, alignment_type=PixelAlignmentType.INNER)
    pixels_df = cone_alignment.pixel_mapping[
        [PixelAlignment.PRIMARY_ORDER_COLUMN_NAME, PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME]
    ]
    filtered_pixels_df = pixels_df.drop_duplicates()
    partition_info_df = filtered_pixels_df.rename(
        columns={
            PixelAlignment.PRIMARY_ORDER_COLUMN_NAME: PartitionInfo.METADATA_ORDER_COLUMN_NAME,
            PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME: PartitionInfo.METADATA_PIXEL_COLUMN_NAME,
        }
    )
    return partition_info_df.reset_index(drop=True)


def _generate_cone_pixel_tree(ra: float, dec: float, radius: float, order: int):
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with a cone"""
    n_side = hp.order2nside(order)
    center_vec = hp.ang2vec(ra, dec, lonlat=True)
    radius_radians = np.radians(radius)
    cone_pixels = hp.query_disc(n_side, center_vec, radius_radians, inclusive=True, nest=True)
    cone_pixel_info_dict = {
        PartitionInfo.METADATA_ORDER_COLUMN_NAME: np.full(len(cone_pixels), order),
        PartitionInfo.METADATA_PIXEL_COLUMN_NAME: cone_pixels,
    }
    cone_partition_info_df = pd.DataFrame.from_dict(cone_pixel_info_dict)
    cone_tree = PixelTreeBuilder.from_partition_info_df(cone_partition_info_df)
    return cone_tree
