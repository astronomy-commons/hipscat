from typing import List

from mocpy import MOC
import astropy.units as u

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.moc_filter import filter_by_moc
from hipscat.pixel_tree.pixel_tree import PixelTree


def filter_pixels_by_cone(
    pixel_tree: PixelTree, ra: float, dec: float, radius_arcsec: float
) -> List[HealpixPixel]:
    """Filter the leaf pixels in a pixel tree to return a partition_info dataframe with the pixels
    that overlap with a cone.

    Args:
        ra (float): Right Ascension of the center of the cone in degrees
        dec (float): Declination of the center of the cone in degrees
        radius_arcsec (float): Radius of the cone in arcseconds

    Returns:
        List of HealpixPixels representing only the pixels that overlap with the specified cone.
    """
    max_order = pixel_tree.get_max_depth()
    cone_moc = generate_cone_moc(ra, dec, radius_arcsec, max_order)
    return filter_by_moc(pixel_tree, cone_moc).get_healpix_pixels()


def generate_cone_moc(ra: float, dec: float, radius_arcsec: float, order: int) -> MOC:
    """Generate a MOC object that covers the cone"""
    return MOC.from_cone(lon=ra * u.deg, lat=dec * u.deg, radius=radius_arcsec * u.arcsec, max_depth=order)
