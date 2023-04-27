from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from hipscat.pixel_math.hipscat_id import HIPSCAT_ID_HEALPIX_ORDER


@dataclass(eq=True, frozen=True, order=True)
class HealpixPixel:
    """A HEALPix pixel, represented by an order and pixel number in NESTED ordering scheme

    see https://lambda.gsfc.nasa.gov/toolbox/pixelcoords.html for more information
    """

    order: int
    pixel: int

    def __post_init__(self) -> None:
        """Initialize a HEALPix pixel
        Args:
            order: HEALPix order
            pixel: HEALPix pixel number in NESTED ordering scheme
        """
        if self.order > HIPSCAT_ID_HEALPIX_ORDER:
            raise ValueError(
                f"HEALPix order cannot be greater than {HIPSCAT_ID_HEALPIX_ORDER}"
            )

    def __str__(self) -> str:
        return f"Order: {self.order}, Pixel: {self.pixel}"

    def __repr__(self):
        return self.__str__()

    def convert_to_lower_order(self, delta_order: int) -> HealpixPixel:
        if self.order - delta_order < 0:
            raise ValueError("Pixel Order cannot be below zero")
        new_order = self.order - delta_order
        new_pixel = math.floor(self.pixel / 4**delta_order)
        return HealpixPixel(new_order, new_pixel)

    def convert_to_higher_order(self, delta_order: int) -> List[HealpixPixel]:
        if self.order + delta_order > HIPSCAT_ID_HEALPIX_ORDER:
            raise ValueError(
                f"Pixel Order cannot be above maximum order {HIPSCAT_ID_HEALPIX_ORDER}"
            )
        pixels = []
        new_order = self.order + delta_order
        for new_pixel in range(self.pixel * 4**delta_order, (self.pixel + 1) * 4**delta_order):
            pixels.append(HealpixPixel(new_order, new_pixel))
        return pixels
