from typing import List

from mocpy import MOC
import astropy.units as u

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.moc_filter import filter_by_moc
from hipscat.pixel_tree.pixel_tree import PixelTree


def generate_cone_moc(ra: float, dec: float, radius_arcsec: float, order: int) -> MOC:
    """Generate a MOC object that covers the cone"""
    return MOC.from_cone(lon=ra * u.deg, lat=dec * u.deg, radius=radius_arcsec * u.arcsec, max_depth=order)
