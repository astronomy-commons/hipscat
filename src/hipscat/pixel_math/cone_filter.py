import healpy as hp
import numpy as np
import pandas as pd

from hipscat.catalog.partition_info import PartitionInfo
from hipscat.pixel_tree import align_trees, PixelAlignmentType, PixelAlignment
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_cone(
        pixel_tree: PixelTree, ra: float, dec: float, radius: float
) -> pd.DataFrame:
    max_order = max(pixel_tree.pixels.keys())
    n_side = hp.order2nside(max_order)
    center_vec = hp.ang2vec(ra, dec, lonlat=True)
    radius_radians = np.radians(radius)
    cone_pixels = hp.query_disc(n_side, center_vec, radius_radians, inclusive=True, nest=True)
    cone_pixel_info_dict = {
        PartitionInfo.METADATA_ORDER_COLUMN_NAME: [max_order for _ in
                                                              range(len(cone_pixels))],
        PartitionInfo.METADATA_PIXEL_COLUMN_NAME: cone_pixels,
    }
    cone_partition_info_df = pd.DataFrame.from_dict(cone_pixel_info_dict)
    cone_tree = PixelTreeBuilder.from_partition_info_df(cone_partition_info_df)
    cone_alignment = align_trees(pixel_tree, cone_tree, alignment_type=PixelAlignmentType.INNER)
    pixels_df = cone_alignment.pixel_mapping[[PixelAlignment.PRIMARY_ORDER_COLUMN_NAME, PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME]]
    filtered_pixels_df = pixels_df.drop_duplicates()
    partition_info_df = filtered_pixels_df.rename(columns={
        PixelAlignment.PRIMARY_ORDER_COLUMN_NAME: PartitionInfo.METADATA_ORDER_COLUMN_NAME,
        PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME: PartitionInfo.METADATA_PIXEL_COLUMN_NAME,
    })
    return partition_info_df.reset_index(drop=True)
