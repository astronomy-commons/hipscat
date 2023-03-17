"""Compute the hipscat ID field"""

import healpy as hp
import numpy as np

HIPSCAT_ID_HEALPIX_ORDER = 19


def compute_hipscat_id(ra_values, dec_values):
    """Compute the hipscat ID field.

    This index is defined as a 64-bit integer which has two parts:
        - healpix pixel (at order 19)
        - incrementing counter (within same healpix, for uniqueness)
    |------------------------------------------|-------------------|
    |<-----    healpixel at order 19    ------>|<--   counter   -->|

    This provides us with an increasing index, that will not overlap
    between spatially partitioned data files.
    """
    if len(ra_values) != len(dec_values):
        raise ValueError("ra and dec arrays should have the same length")

    ## Construct the bit-shifted healpix segment
    value_count = len(ra_values)
    mapped_pixels = hp.ang2pix(
        2**HIPSCAT_ID_HEALPIX_ORDER, ra_values, dec_values, nest=True, lonlat=True
    )
    shifted_pixels = mapped_pixels.astype(np.uint64) << (
        64 - (4 + 2 * HIPSCAT_ID_HEALPIX_ORDER)
    )

    ## We sort to put pixels next to each other that will need to be counted.
    ## This simplifies the counter logic, as we can subtract the index where
    ## we first see the pixel value from the current index to get the offset counter.
    sort_index = np.argsort(shifted_pixels)
    shifted_pixels = shifted_pixels[sort_index]
    _, unique_inverses, unique_indexes = np.unique(
        shifted_pixels, return_inverse=True, return_index=True
    )

    ## Construct the counter.
    unique_inverses = unique_inverses.astype(np.uint64)
    boring_number_index = np.arange(value_count, dtype=np.uint64)
    offset_counter = boring_number_index - unique_inverses[unique_indexes]
    shifted_pixels = shifted_pixels + offset_counter

    ## Map back to the original, unsorted, values
    unsort_index = np.argsort(sort_index)
    return shifted_pixels[unsort_index]


def hipscat_id_to_healpix(ids):
    """Convert some hipscat ids to the healpix pixel at order 19.
    This is just bit-shifting the counter away.
    """
    return np.asarray(ids, dtype=np.uint64) >> (64 - (4 + 2 * HIPSCAT_ID_HEALPIX_ORDER))
