from __future__ import annotations

from typing import Tuple, Union

from hipscat.pixel_math.healpix_pixel import HealpixPixel

HealpixInputTypes = Union[HealpixPixel, Tuple[int, int]]


def get_healpix_pixel(pixel: HealpixInputTypes) -> HealpixPixel:
    """Function to convert argument of either HealpixPixel or a tuple of (order, pixel) to a
    HealpixPixel

    Args:
        pixel: an object to be converted to a HealpixPixel object
    """

    if isinstance(pixel, tuple):
        if len(pixel) != 2:
            raise ValueError("Tuple must contain two values: HEALPix order and HEALPix pixel number")
        return HealpixPixel(order=pixel[0], pixel=pixel[1])
    if isinstance(pixel, HealpixPixel):
        return pixel
    raise TypeError("pixel must either be of type `HealpixPixel` or tuple (order, pixel)")
