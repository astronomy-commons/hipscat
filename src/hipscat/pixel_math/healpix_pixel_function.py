from typing import List

import numpy as np

from hipscat.pixel_math.healpix_pixel import HealpixPixel


def get_pixel_argsort(pixels: List[HealpixPixel]):
    """Perform an indirect sort of a list of HealpixPixels.

    This will order the pixels according to a breadth-first traversal of the healpix
    pixel hierarchy, not merely by increasing order by Norder/Npix (depth-first ordering).
    This is similar to ordering fully by _hipscat_index.

    Args:
        pixels (List[HealpixPixel]): array to sort

    Returns:
        array of indices that sort the pixels in breadth-first order.
    """
    if pixels is None or len(pixels) == 0:
        return []
    # Construct a parallel list of exploded, high order pixels.
    highest_order = np.max(pixels).order

    constant_breadth_pixel = [pixel.pixel * (4 ** (highest_order - pixel.order)) for pixel in pixels]

    # Get the argsort of the higher order array.
    return np.argsort(constant_breadth_pixel, kind="stable")


def get_pixels_from_intervals(intervals: np.ndarray, tree_order: int) -> np.ndarray:
    if intervals.shape[1] == 0:
        return np.empty((2, 0), dtype=np.int64)
    orders = tree_order - ((np.vectorize(lambda x: int(x).bit_length())(intervals[1] - intervals[0]) - 1) >> 1)
    pixels = intervals[0] >> 2 * (tree_order - orders)
    return np.array([orders, pixels])
