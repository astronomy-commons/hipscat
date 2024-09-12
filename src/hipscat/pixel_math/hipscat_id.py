"""
Compute the hipscat index field

This index is defined as a 64-bit integer which has two parts:
    - healpix pixel (at order 19)
    - incrementing counter (within same healpix, for uniqueness)

::

    |------------------------------------------|-------------------|
    |<-----    healpixel at order 19    ------>|<--   counter   -->|

This provides us with an increasing index, that will not overlap
between spatially partitioned data files.

See the README in this directory for more information on the fiddly pixel math.
"""

from __future__ import annotations

from typing import List

import numpy as np

import hipscat.pixel_math.healpix_shim as hp

HIPSCAT_ID_COLUMN = "_hipscat_index"
HIPSCAT_ID_HEALPIX_ORDER = 19
HIPSCAT_ID_MAX = 2**64 - 1


def compute_hipscat_id(ra_values: List[float], dec_values: List[float]) -> np.ndarray:
    """Compute the hipscat ID field.

    Args:
        ra_values (List[float]): celestial coordinates, right ascension
        dec_values (List[float]): celestial coordinates, declination
    Returns:
        one-dimensional numpy array of int64s with hipscat IDs for the sky positions.
    Raises:
        ValueError: if the length of the input lists don't match.
    """
    if len(ra_values) != len(dec_values):
        raise ValueError("ra and dec arrays should have the same length")

    ## Construct the bit-shifted healpix segment
    value_count = len(ra_values)
    mapped_pixels = hp.ang2pix(2**HIPSCAT_ID_HEALPIX_ORDER, ra_values, dec_values, nest=True, lonlat=True)

    ## We sort to put pixels next to each other that will need to be counted.
    ## This simplifies the counter logic, as we can subtract the index where
    ## we first see the pixel value from the current index to get the offset counter.
    sort_index = np.argsort(mapped_pixels, kind="stable")
    mapped_pixels = mapped_pixels[sort_index]

    ## Construct the counter.
    _, unique_indices, unique_inverse = np.unique(mapped_pixels, return_inverse=True, return_index=True)
    unique_indices = unique_indices.astype(np.uint64)
    boring_number_index = np.arange(value_count, dtype=np.uint64)
    offset_counter = boring_number_index - unique_indices[unique_inverse]

    ## Add counter to shifted pixel, and map back to the original, unsorted, values
    shifted_pixels = _compute_hipscat_id_from_mapped_pixels(mapped_pixels, offset_counter)

    unsort_index = np.argsort(sort_index, kind="stable")
    return shifted_pixels[unsort_index]


def _compute_hipscat_id_from_mapped_pixels(mapped_pixels, offset_counter):
    shifted_pixels = mapped_pixels.astype(np.uint64) << np.uint64(64 - (4 + 2 * HIPSCAT_ID_HEALPIX_ORDER))
    shifted_pixels = shifted_pixels + offset_counter
    return shifted_pixels


def hipscat_id_to_healpix(ids: List[int], target_order: int = HIPSCAT_ID_HEALPIX_ORDER) -> np.ndarray:
    """Convert some hipscat ids to the healpix pixel at the specified order
    This is just bit-shifting the counter away.

    Args:
        ids (List[int64]): list of well-formatted hipscat ids
        target_order (int64): Defaults to `HIPSCAT_ID_HEALPIX_ORDER`.
            The order of the pixel to get from the hipscat ids.
    Returns:
        numpy array of target_order pixels from the hipscat id
    """
    return np.asarray(ids, dtype=np.uint64) >> (64 - (4 + 2 * target_order))


def healpix_to_hipscat_id(
    order: int | List[int], pixel: int | List[int], counter: int | List[int] = 0
) -> np.uint64 | np.ndarray:
    """Convert a healpix pixel to a hipscat_id

    This maps the healpix pixel to the lowest pixel number within that pixel at order 19,
    then shifts and adds the given counter to get a hipscat_id.

    Useful for operations such as filtering by hipscat_id.

    Args:
        order (int64 | List[int64]): order of pixel to convert
        pixel (int64 | List[int64]): pixel number in nested ordering of pixel to convert
        counter (int64 | List[int64]) (Default: 0): counter value in converted hipscat id
    Returns:
        hipscat id or numpy array of hipscat ids
    """
    order = np.uint64(order)
    pixel = np.uint64(pixel)
    counter = np.uint64(counter)
    pixel_higher_order = pixel * (4 ** (HIPSCAT_ID_HEALPIX_ORDER - order))
    hipscat_id = _compute_hipscat_id_from_mapped_pixels(pixel_higher_order, counter)
    return hipscat_id
