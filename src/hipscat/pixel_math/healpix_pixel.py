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
            raise ValueError(f"HEALPix order cannot be greater than {HIPSCAT_ID_HEALPIX_ORDER}")

    def __str__(self) -> str:
        return f"Order: {self.order}, Pixel: {self.pixel}"

    def __repr__(self):
        return self.__str__()

    def convert_to_lower_order(self, delta_order: int) -> HealpixPixel:
        """Returns the HEALPix pixel that contains the pixel at a lower order

        Args:
            delta_order: the difference in order to be subtracted from the current order to generate
                the pixel at a lower order. Must be non-negative

        Returns:
            A new `HealpixPixel` at the current order - `delta_order` which contains the current
            pixel

        Raises:
            ValueError: If delta_order is greater than the current order, a pixel cannot be
                generated at a negative order. Or if delta_order is negative

        """
        if self.order - delta_order < 0:
            raise ValueError("Pixel Order cannot be below zero")
        if delta_order < 0:
            raise ValueError("delta order cannot be below zero")
        new_order = self.order - delta_order
        new_pixel = math.floor(self.pixel / 4**delta_order)
        return HealpixPixel(new_order, new_pixel)

    def convert_to_higher_order(self, delta_order: int) -> List[HealpixPixel]:
        """Returns a list of HEALPix pixels making up the current pixel at a higher order

        Args:
            delta_order: the difference in order to be added to the current order to generate the
                pixels at a higher order. Must be non-negative

        Returns:
            A new `HealpixPixel` at the current order - `delta_order` which contains the current
            pixel

        Raises:
            ValueError: If delta_order + current order is greater than the maximum HEALPix order,
                pixels cannot be  generated. Or if delta_order is negative
        """
        if self.order + delta_order > HIPSCAT_ID_HEALPIX_ORDER:
            raise ValueError(f"Pixel Order cannot be above maximum order {HIPSCAT_ID_HEALPIX_ORDER}")
        if delta_order < 0:
            raise ValueError("delta order cannot be below zero")
        pixels = []
        new_order = self.order + delta_order
        for new_pixel in range(self.pixel * 4**delta_order, (self.pixel + 1) * 4**delta_order):
            pixels.append(HealpixPixel(new_order, new_pixel))
        return pixels
