from __future__ import annotations

from dataclasses import dataclass

import hipscat.pixel_math.hipscat_id

MAXIMUM_ORDER = hipscat.pixel_math.hipscat_id.HIPSCAT_ID_HEALPIX_ORDER


@dataclass
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

    def _key(self) -> tuple[int, int]:
        """Returns tuple of order and pixel, for use in hashing and equality"""
        return self.order, self.pixel

    def __eq__(self, other: object) -> bool:
        """Defines 2 pixels as equal if they have the same order and pixel"""
        if not isinstance(other, HealpixPixel):
            return False
        return self._key() == other._key()

    def __hash__(self) -> int:
        """Hashes pixels by order and pixel, so equal pixel objects are looked up the same in
        hashable data structures"""
        return hash(self._key())

    def __str__(self) -> str:
        return f"Order: {self.order}, Pixel: {self.pixel}"

    def __repr__(self):
        return self.__str__()
