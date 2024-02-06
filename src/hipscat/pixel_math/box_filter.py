from __future__ import annotations

from typing import List, Tuple

import astropy.units as u
import healpy as hp
import numpy as np
from astropy.coordinates import Angle

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.filter import get_filtered_pixel_list
from hipscat.pixel_math.polygon_filter import SphericalCoordinates
from hipscat.pixel_tree import PixelAlignmentType, align_trees
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_box(
    pixel_tree: PixelTree, ra: Tuple[float, float] | None, dec: Tuple[float, float] | None
) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a partition_info dataframe
    with the pixels that overlap with a right ascension and/or declination region.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from
        ra (Tuple[float, float]): Right ascension range, in [0,360] degrees
        dec (Tuple[float, float]): Declination range, in [-90,90] degrees

    Returns:
        List of HEALPix representing only the pixels that overlap with the right
        ascension and/or declination region.
    """
    max_order = pixel_tree.get_max_depth()

    filter_tree = None
    ra_search_tree, dec_search_tree = None, None

    if ra is not None:
        ra_search_tree = _generate_ra_strip_pixel_tree(ra, max_order)
        filter_tree = ra_search_tree
    if dec is not None:
        dec_search_tree = _generate_dec_strip_pixel_tree(dec, max_order)
        filter_tree = dec_search_tree
    if ra_search_tree is not None and dec_search_tree is not None:
        filter_tree = align_trees(
            ra_search_tree, dec_search_tree, alignment_type=PixelAlignmentType.INNER
        ).pixel_tree

    result_pixels = get_filtered_pixel_list(pixel_tree, filter_tree)

    return result_pixels


def wrap_ra_values(ra: Tuple[float, float] | None) -> Tuple[float, float] | None:
    """Wraps right ascension values to the [0,360] degree range.

    Args:
        ra (Tuple[float, float]): The right ascension values, in degrees

    Returns:
        The right ascension values wrapped to the [0,360] degree range,
        or None if they do not exist.
    """
    return tuple(wrap_angles(list(ra))) if ra else None


def wrap_angles(ra: List[float]) -> List[float]:
    """Wraps angles to the [0,360] degree range.

    Arguments:
        ra (List[float]): List of right ascension values

    Returns:
        A list of right ascension values, wrapped to the [0,360] degree range.
    """
    return Angle(ra, u.deg).wrap_at(360 * u.deg).degree


def _generate_ra_strip_pixel_tree(ra_range: Tuple[float, float], order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with the ra region."""
    # Subdivide polygons (if needed) in two smaller polygons of at most 180 degrees
    division_ra = _get_division_ra(ra_range)

    if division_ra is not None:
        pixels_in_range = _get_pixels_for_subpolygons(
            [
                # North Pole
                [(0, 90), (ra_range[0], 0), (division_ra, 0)],
                [(0, 90), (division_ra, 0), (ra_range[1], 0)],
                # South Pole
                [(ra_range[0], 0), (0, -90), (division_ra, 0)],
                [(division_ra, 0), (0, -90), (ra_range[1], 0)],
            ],
            order,
        )
    else:
        # HEALpy will assume the polygon of smallest area by default
        # e.g. for ra_ranges of [10,50], [200,10] or [350,10]
        pixels_in_range = _get_pixels_for_subpolygons(
            [
                # North Pole
                [(0, 90), (ra_range[0], 0), (ra_range[1], 0)],
                # South Pole
                [(ra_range[0], 0), (0, -90), (ra_range[1], 0)],
            ],
            order,
        )

    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in pixels_in_range]
    return PixelTreeBuilder.from_healpix(pixel_list)


def _generate_dec_strip_pixel_tree(dec_range: Tuple[float, float], order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap with the dec region."""
    nside = hp.order2nside(order)
    # Convert declination values to colatitudes, in radians, and revert their order
    colat_rad = np.sort(np.radians([90 - dec if dec > 0 else 90 + abs(dec) for dec in dec_range]))
    # Figure out which pixels in nested order are contained in the declination band
    pixels_in_range = hp.ring2nest(
        nside, hp.query_strip(nside, theta1=colat_rad[0], theta2=colat_rad[1], inclusive=True)
    )
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in pixels_in_range]
    return PixelTreeBuilder.from_healpix(pixel_list)


def _get_division_ra(ra_range: Tuple[float, float]) -> float | None:
    """Gets the division angle for the right ascension region. This is crucial for the edge
    cases where we need to split up polygons wider than 180 degrees into smaller polygons."""
    division_ra = None
    if ra_range[0] > ra_range[1] and 360 - ra_range[0] + ra_range[1] >= 180:
        # e.g. edge case of [350, 170] or [180, 0], we want the wider polygon
        division_ra = (ra_range[1] - 360 + ra_range[0]) / 2
    elif ra_range[0] < ra_range[1] and ra_range[1] - ra_range[0] >= 180:
        # e.g. edge case of [10, 200] or [0, 180], we want the wider polygon
        division_ra = ra_range[0] + (ra_range[1] - ra_range[0]) / 2
    return division_ra


def _get_pixels_for_subpolygons(polygons: List[List[SphericalCoordinates]], order: int) -> np.ndarray:
    """Gets the unique pixels for a set of sub-polygons."""
    nside = hp.order2nside(order)
    all_polygon_pixels = []
    for vertices in polygons:
        vertices = hp.ang2vec(*np.array(vertices).T, lonlat=True)
        pixels = hp.query_polygon(nside, vertices, inclusive=True, nest=True)
        all_polygon_pixels.append(pixels)
    return np.unique(np.concatenate(all_polygon_pixels, 0))
