from __future__ import annotations

from typing import List, Tuple

import healpy as hp
import numpy as np
from mocpy import MOC
from typing_extensions import TypeAlias

import astropy.units as u

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.moc_filter import filter_by_moc
from hipscat.pixel_tree.pixel_tree import PixelTree

# Pair of spherical sky coordinates (ra, dec)
SphericalCoordinates: TypeAlias = Tuple[float, float]

# Sky coordinates on the unit sphere, in cartesian representation (x,y,z)
CartesianCoordinates: TypeAlias = Tuple[float, float, float]


def filter_pixels_by_polygon(
    pixel_tree: PixelTree, vertices: List[CartesianCoordinates]
) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a list of healpix pixels that
    overlap with a polygonal region.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from.
        vertices (List[CartesianCoordinates]): The vertices of the polygon to filter points
            with, in lists of (x,y,z) points on the unit sphere.

    Returns:
        List of HealpixPixel, representing only the pixels that overlap
        with the specified polygonal region, and the maximum pixel order.
    """
    vertices = np.array(vertices)
    max_order = pixel_tree.get_max_depth()
    polygon_moc = generate_polygon_moc(vertices, max_order)
    return filter_by_moc(pixel_tree, polygon_moc).get_healpix_pixels()


def generate_polygon_moc(vertices: np.array, order: int) -> MOC:
    """Generates a moc filled with leaf nodes at a given order that overlap within
    a polygon. Vertices is an array of Spherical coordinates, in representation (ra,dec)
    and shape (Num vertices, 2), representing the vertices of the polygon."""
    polygon_pixels = hp.query_polygon(hp.order2nside(order), vertices, inclusive=True, nest=True)
    polygon_orders = np.full(len(polygon_pixels), fill_value=order)
    return MOC.from_healpix_cells(ipix=polygon_pixels, depth=polygon_orders, max_depth=order)
