from typing import List, Tuple

import healpy as hp
import numpy as np
from regions import PolygonSkyRegion
from regions.core.attributes import OneDSkyCoord

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.filter import get_filtered_pixel_list
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_polygon(
        pixel_tree: PixelTree, polygon: PolygonSkyRegion
) -> Tuple[List[HealpixPixel], int]:
    """Filter the leaf pixels in a pixel tree to return a list of
    healpix pixels that overlap with a polygonal region.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from
        polygon (PolygonSkyRegion): The polygon to filter pixels with. Its
            vertices are specified in sky coordinates (ra, dec).

    Returns:
        List of HealpixPixel, representing only the pixels that overlap
        with the specified polygonal region, and the maximum pixel order.
    """
    max_order = max(pixel_tree.pixels.keys())
    polygon_tree = _generate_polygon_pixel_tree(polygon.vertices, max_order)
    pixel_list = get_filtered_pixel_list(pixel_tree, polygon_tree)
    return pixel_list, max_order


def _generate_polygon_pixel_tree(vertices: OneDSkyCoord, order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap within a polygon"""
    # The cartesian representation of coordinates is represented in arrays of ra and dec.
    # To obtain the coordinates to use in query_polygon we need to calculate the array transpose.
    vertices_coords = np.array(vertices.cartesian.xyz).T
    polygon_pixels = hp.query_polygon(hp.order2nside(order), vertices_coords, inclusive=True, nest=True)
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in polygon_pixels]
    return PixelTreeBuilder.from_healpix(pixel_list)
