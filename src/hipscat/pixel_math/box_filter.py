from __future__ import annotations

from typing import List, Tuple

import astropy.units as u
import healpy as hp
import numpy as np
from astropy.coordinates import Angle

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.filter import get_filtered_pixel_list
from hipscat.pixel_math.polygon_filter import SphericalCoordinates
from hipscat.pixel_math.validators import validate_box_search
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_box(
    pixel_tree: PixelTree, ra: Tuple[float, float] | None, dec: Tuple[float, float] | None
) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a partition_info dataframe
    with the pixels that overlap with a right ascension or the declination region.
    Only one of ra and dec should be set, otherwise one should use polygonal search.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from
        ra (Tuple[float, float]): Right ascension range, in degrees
        dec (Tuple[float, float]): Declination range, in degrees

    Returns:
        List of HealpixPixels representing only the pixels that overlap with the right
        ascension or the declination region.
    """
    validate_box_search(ra, dec)
    max_order = pixel_tree.get_max_depth()
    search_tree = (
        _generate_ra_strip_pixel_tree(ra, max_order)
        if ra is not None
        else _generate_dec_strip_pixel_tree(dec, max_order)
    )
    return get_filtered_pixel_list(pixel_tree, search_tree)


def transform_radec(
    ra: Tuple[float, float] | None, dec: Tuple[float, float] | None
) -> Tuple[Tuple[float, float] | None, Tuple[float, float] | None]:
    """Transforms ra and dec values so that they are valid when performing the
    search. Wraps right ascension values to the [0,360] degree range and sorts
    declination values by ascending order."""
    if ra is not None:
        ra = tuple(wrap_angles(list(ra)))
    if dec is not None:
        dec = tuple(np.sort(dec))
    return ra, dec


def wrap_angles(ra: List[float]) -> List[float]:
    """Wraps angles to the [0,360] degree range.

    Arguments:
        ra (List[float]): List of right ascension values

    Returns:
        A list of right ascension values, wrapped to the [0,360] degree range.
    """
    return Angle(ra, u.deg).wrap_at(360 * u.deg).degree


def form_polygon(ra: Tuple[float, float], dec: Tuple[float, float]) -> List[SphericalCoordinates]:
    """Checks if both ra and dec were provided and calculates the polygon vertices.
    Right ascension values should have been wrapped to the [0,360] degree range and
    declination values sorted in ascending order.

    Returns:
        A list of polygon vertices, in spherical coordinates.
    """
    return [(ra[0], dec[0]), (ra[0], dec[1]), (ra[1], dec[1]), (ra[1], dec[0])]


def _generate_ra_strip_pixel_tree(ra_range: Tuple[float, float], order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with the ra region."""
    nside = hp.order2nside(order)
    # The first region contains the North Pole
    vertices_1 = [(0, 90), (ra_range[0], 0), (ra_range[1], 0)]
    vertices_1 = hp.ang2vec(*np.array(vertices_1).T, lonlat=True)
    pixels_in_range_1 = hp.query_polygon(nside, vertices_1, inclusive=True, nest=True)
    # The second region contains the South Pole
    vertices_2 = [(ra_range[0], 0), (0, -90), (ra_range[1], 0)]
    vertices_2 = hp.ang2vec(*np.array(vertices_2).T, lonlat=True)
    pixels_in_range_2 = hp.query_polygon(nside, vertices_2, inclusive=True, nest=True)
    # Merge the two sets of pixels
    pixels_in_range = np.unique(np.concatenate((pixels_in_range_1, pixels_in_range_2), 0))
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in pixels_in_range]
    return PixelTreeBuilder.from_healpix(pixel_list)


def _generate_dec_strip_pixel_tree(dec_range: Tuple[float, float], order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with the dec region."""
    nside = hp.order2nside(order)
    sorted_dec = np.sort([90 - dec if dec > 0 else 90 + abs(dec) for dec in dec_range])
    min_colatitude = np.radians(sorted_dec[0])
    max_colatitude = np.radians(sorted_dec[1])
    pixels_in_range = hp.ring2nest(
        nside, hp.query_strip(nside, theta1=min_colatitude, theta2=max_colatitude, inclusive=True)
    )
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in pixels_in_range]
    return PixelTreeBuilder.from_healpix(pixel_list)
