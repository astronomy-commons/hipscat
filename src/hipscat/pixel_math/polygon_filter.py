from typing import List

import healpy as hp
import numpy as np

from spherical_geometry.polygon import SingleSphericalPolygon

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.filter import get_filtered_pixel_list
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def filter_pixels_by_polygon(pixel_tree: PixelTree, polygon: SingleSphericalPolygon) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a list of
    healpix pixels that overlap with a polygonal region.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from
        polygon (SingleSphericalPolygon): The polygon to filter pixels with

    Returns:
        List of HealpixPixel, representing only the pixels that overlap
        with the specified polygonal region, and the maximum pixel order.
    """
    max_order = max(pixel_tree.pixels.keys())
    cartesian_vertices = _get_polygon_cartesian_vertices(polygon)
    polygon_tree = _generate_polygon_pixel_tree(cartesian_vertices, max_order)
    return get_filtered_pixel_list(pixel_tree, polygon_tree)


def _get_polygon_cartesian_vertices(polygon: SingleSphericalPolygon) -> np.array:
    """Extracts the polygon coordinates in cartesian representation.

    The SphericalPolygon is an explicitly closed polygon, meaning that the
    first and last vertices are the same. Only the first of the repeated
    vertices is kept.

    Args:
        polygon (SphericalPolygon): The sky polygon to filter points with

    Returns:
        An array of 3D coordinates, in cartesian representation (x,y,z) and
        shape (Num vertices, 3), representing the vertices of the polygon.
    """
    xyz_vertices = list(polygon.points)[0]
    return np.array(xyz_vertices)[:-1]


def _generate_polygon_pixel_tree(vertices: np.array, order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap within a polygon"""
    polygon_pixels = hp.query_polygon(hp.order2nside(order), vertices, inclusive=True, nest=True)
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in polygon_pixels]
    return PixelTreeBuilder.from_healpix(pixel_list)
