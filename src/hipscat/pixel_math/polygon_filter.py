from dataclasses import dataclass
from typing import List, NewType, Tuple

import healpy as hp
from regions.core.attributes import OneDSkyCoord

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree import PixelAlignment, PixelAlignmentType, align_trees
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder
from regions import PolygonSkyRegion


def filter_pixels_by_polygon(pixel_tree: PixelTree, polygon: PolygonSkyRegion) -> Tuple[HealpixPixel, int]:
    """Filter the leaf pixels in a pixel tree to return a partition_info
    dataframe with the pixels that overlap with the polygonal region.

    Args:
        pixel_tree (PixelTree): The catalog tree to filter pixels from.
        polygon (SkyPolygon): The polygon to filter pixels with. Its
            vertices are specified in sky coordinates (ra, dec).

    Returns:
        List of HealpixPixels, representing only the pixels that overlap
        with the specified polygonal region, and the maximum pixel order
    """
    max_order = 10 if max(pixel_tree.pixels.keys()) < 10 else max(pixel_tree.pixels.keys())
    polygon_tree = _generate_polygon_pixel_tree(polygon.vertices, max_order)
    polygon_alignment = align_trees(pixel_tree, polygon_tree, alignment_type=PixelAlignmentType.INNER)
    pixels_df = polygon_alignment.pixel_mapping[
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
    return pixel_list, max_order


def _generate_polygon_pixel_tree(vertices: OneDSkyCoord, order: int) -> PixelTree:
    """Generates a pixel_tree filled with leaf nodes at a given order that overlap within a polygon"""
    n_side = hp.order2nside(order)
    polygon_pixels = hp.query_polygon(n_side, vertices, inclusive=True, nest=True)
    pixel_list = [HealpixPixel(order, polygon_pixel) for polygon_pixel in polygon_pixels]
    polygon_tree = PixelTreeBuilder.from_healpix(pixel_list)
    return polygon_tree
