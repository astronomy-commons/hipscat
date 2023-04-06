from __future__ import annotations

from dataclasses import dataclass

import hipscat.pixel_math.hipscat_id

MAXIMUM_ORDER = hipscat.pixel_math.hipscat_id.HIPSCAT_ID_HEALPIX_ORDER


@dataclass(eq=True, frozen=True)
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
        if self.order > MAXIMUM_ORDER:
            raise ValueError(f"HEALPix order cannot be greater than {MAXIMUM_ORDER}")

    def __str__(self) -> str:
        return f"Order: {self.order}, Pixel: {self.pixel}"

    def __repr__(self):
        return self.__str__()
