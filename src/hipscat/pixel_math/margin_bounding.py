"""Utilities to build bounding boxes around healpixels that include a neighor margin."""

import healpy as hp
import numpy as np

def get_margin_scale(pixel_order, margin_threshold=0.1):
    """Get the scale value need to expand the pixel bounding box to include the `margin_threshold`.

    Args:
        pixel_order (int): the order of the pixel to which we're calculating the margin region for.
        margin_threshold (float): the size of the border region in degrees.
    Returns:
        a float representing the scale factor.
    """
    if margin_threshold <= 0.:
        raise ValueError("margin_threshold must be greater than 0.")
    
    resolution = hp.nside2resol(2**pixel_order, arcmin=True) / 60.
    resolution_and_thresh = resolution + (margin_threshold)
    margin_area = resolution_and_thresh ** 2
    pixel_area = hp.pixelfunc.nside2pixarea(2**pixel_order, degrees=True)
    scale = margin_area / pixel_area
    return scale