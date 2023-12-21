from typing import List, Tuple, TypeAlias

import healpy as hp
import numpy as np

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.filter import get_filtered_pixel_list
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder

# Pair of sky coordinates (ra, dec)
SkyCoordinates: TypeAlias = Tuple[float, float]

# Sky coordinates on the unit sphere, in cartesian representation (x,y,z)
CartesianCoordinates: TypeAlias = Tuple[float, float, float]


def filter_pixels_by_polygon(
    pixel_tree: PixelTree, vertices: List[CartesianCoordinates]
) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a list of healpix pixels that
    overlap with a polygonal region.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from.
        vertices (List[CartesianCoordinates]): The vertices of the polygon to filter pixels
            with, in cartesian representation, with shape (Num vertices, 3).

    Returns:
        List of HealpixPixel, representing only the pixels that overlap
        with the specified polygonal region, and the maximum pixel order.
    """
    max_order = max(pixel_tree.pixels.keys())
    polygon_tree = _generate_polygon_pixel_tree(vertices, max_order)
    return get_filtered_pixel_list(pixel_tree, polygon_tree)


def _generate_polygon_pixel_tree(vertices: np.array, order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap within
    a polygon. Vertices is an array of 3D coordinates, in cartesian representation (x,y,z)
    and shape (Num vertices, 3), representing the vertices of the polygon."""
    polygon_pixels = hp.query_polygon(hp.order2nside(order), vertices, inclusive=True, nest=True)
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in polygon_pixels]
    return PixelTreeBuilder.from_healpix(pixel_list)
