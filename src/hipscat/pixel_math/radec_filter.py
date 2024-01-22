from typing import List, Tuple

import healpy as hp
import numpy as np

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.filter import get_filtered_pixel_list
from hipscat.pixel_tree.pixel_tree import PixelTree


def filter_pixels_by_radec(
    pixel_tree: PixelTree, ra: Tuple[float, float], dec: Tuple[float, float]
) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a partition_info dataframe
    with the pixels that overlap with a right ascension or the declination region.
    Only one of ra and dec must be set, otherwise use polygonal_search.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from
        ra (Tuple[float, float]): Right Ascension range, in degrees
        dec (Tuple[float, float]): Declination range, in degrees

    Returns:
        List of HealpixPixels representing only the pixels that overlap with the right
        ascension or the declination region.
    """
    max_order = pixel_tree.get_max_depth()
    if ra is not None and dec is not None:
        raise ValueError("Use polygonal search")
    if ra is not None:
        pixel_tree = _generate_ra_strip_pixel_tree(ra, max_order)
    elif dec is not None:
        pixel_tree = _generate_dec_strip_pixel_tree(dec, max_order)
    return get_filtered_pixel_list(pixel_tree, pixel_tree)


def _generate_ra_strip_pixel_tree(ra_range: Tuple[float, float], order: int):
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with the ra region"""
    nside = hp.order2nside(order)
    # The first region contains the north pole
    vertices_1 = [(0, 90), (ra_range[0], 0), (ra_range[1], 0)]
    vertices_1 = hp.ang2vec(*np.array(vertices_1).T, lonlat=True)
    pixels_in_range_1 = hp.query_polygon(nside, vertices_1, inclusive=True, nest=True)
    # The second contains the south pole
    vertices_2 = [(ra_range[0], 0), (0, -90), (ra_range[1], 0)]
    vertices_2 = hp.ang2vec(*np.array(vertices_2).T, lonlat=True)
    pixels_in_range_2 = hp.query_polygon(nside, vertices_2, inclusive=True, nest=True)
    # Merge the two sets of pixels
    pixels_in_range = np.unique(np.concatenate((pixels_in_range_1, pixels_in_range_2), 0))
    return [HealpixPixel(order, polygon_pixel) for polygon_pixel in pixels_in_range]


def _generate_dec_strip_pixel_tree(dec_range: Tuple[float, float], order: int):
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with the dec region"""
    nside = hp.order2nside(order)
    sorted_dec = np.sort([90 - dec if dec > 0 else 90 + abs(dec) for dec in dec_range])
    min_colatitude = np.radians(sorted_dec[0])
    max_colatitude = np.radians(sorted_dec[1])
    pixels_in_range = hp.ring2nest(
        nside, hp.query_strip(nside, theta1=min_colatitude, theta2=max_colatitude, inclusive=True)
    )
    return [HealpixPixel(order, polygon_pixel) for polygon_pixel in pixels_in_range]
