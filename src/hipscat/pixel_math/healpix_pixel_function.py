import numpy as np

from hipscat.pixel_math.healpix_pixel import HealpixPixel


def get_pixel_argsort(pixels: list[HealpixPixel]):
    """Perform an indirect sort of a list of HealpixPixels.

    This will order the pixels according to their healpix sky position, not merely
    by increasing order. This is similar to ordering fully by _hipscat_index.

    Args:
        pixels (List[HealpixPixel]): array to sort

    Returns:
        array of indices that sort the pixels in sky order.
    """
    # Construct a parallel list of exploded, high order pixels.
    highest_order = np.max(pixels).order

    sky_position = [pixel.pixel * (4 ** (highest_order - pixel.order)) for pixel in pixels]

    # Get the argsort of the higher order array.
    return np.argsort(sky_position, kind="stable")
