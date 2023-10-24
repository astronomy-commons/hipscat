from typing import List

import healpy as hp
import numpy as np

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree import PixelAlignment, PixelAlignmentType, align_trees
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_cone(pixel_tree: PixelTree, ra: float, dec: float, radius: float) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a partition_info dataframe with the pixels
    that overlap with a cone

    Args:
        ra (float): Right Ascension of the center of the cone in degrees
        dec (float): Declination of the center of the cone in degrees
        radius (float): Radius of the cone in degrees

    Returns:
        List of HealpixPixels representing only the pixels that overlap with the specified cone
    """
    max_order = max(pixel_tree.pixels.keys())
    cone_tree = _generate_cone_pixel_tree(ra, dec, radius, max_order)
    cone_alignment = align_trees(pixel_tree, cone_tree, alignment_type=PixelAlignmentType.INNER)
    pixels_df = cone_alignment.pixel_mapping[
        [PixelAlignment.PRIMARY_ORDER_COLUMN_NAME, PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME]
    ]
    filtered_pixels_df = pixels_df.drop_duplicates()

    pixel_list = [
        HealpixPixel(order, pixel)
        for order, pixel in zip(
            filtered_pixels_df[PixelAlignment.PRIMARY_ORDER_COLUMN_NAME],
            filtered_pixels_df[PixelAlignment.PRIMARY_PIXEL_COLUMN_NAME],
        )
    ]
    return pixel_list


def _generate_cone_pixel_tree(ra: float, dec: float, radius: float, order: int):
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with a cone"""
    n_side = hp.order2nside(order)
    center_vec = hp.ang2vec(ra, dec, lonlat=True)
    radius_radians = np.radians(radius)
    cone_pixels = hp.query_disc(n_side, center_vec, radius_radians, inclusive=True, nest=True)
    pixel_list = [HealpixPixel(order, cone_pixel) for cone_pixel in cone_pixels]
    cone_tree = PixelTreeBuilder.from_healpix(pixel_list)
    return cone_tree
