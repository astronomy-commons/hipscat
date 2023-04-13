from __future__ import annotations

from dataclasses import dataclass

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
