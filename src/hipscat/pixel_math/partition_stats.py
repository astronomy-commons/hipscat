"""Utilities for generating and manipulating object count histograms"""

import healpy as hp
import numpy as np
import pandas as pd

from hipscat.pixel_math.healpix_pixel import HealpixPixel


def empty_histogram(highest_order):
    """Use numpy to create an histogram array with the right shape, filled with zeros.

    Args:
        highest_order (int): the highest healpix order (e.g. 0-10)
    Returns:
        one-dimensional numpy array of long integers, where the length is equal to
        the number of pixels in a healpix map of target order, and all values are set to 0.
    """
    return np.zeros(hp.order2npix(highest_order), dtype=np.int64)


def generate_histogram(
    data: pd.DataFrame,
    highest_order,
    ra_column="ra",
    dec_column="dec",
):
    """Generate a histogram of counts for objects found in `data`

    Args:
        data (:obj:`pd.DataFrame`): tabular object data
        highest_order (int):  the highest healpix order (e.g. 0-10)
        ra_column (str): where in the input to find the celestial coordinate, right ascension
        dec_column (str): where in the input to find the celestial coordinate, declination
    Returns:
        one-dimensional numpy array of long integers where the value at each index corresponds
        to the number of objects found at the healpix pixel.
    Raises:
        ValueError: if the `ra_column` or `dec_column` cannot be found in the input file.
    """
    histogram_result = empty_histogram(highest_order)

    # Verify that the data frame has columns with desired names.
    required_columns = [ra_column, dec_column]
    if not all(x in data.columns for x in required_columns):
        raise ValueError(f"Invalid column names in input: {ra_column}, {dec_column}")
    mapped_pixels = hp.ang2pix(
        2**highest_order,
        data[ra_column].values,
        data[dec_column].values,
        lonlat=True,
        nest=True,
    )
    mapped_pixel, count_at_pixel = np.unique(mapped_pixels, return_counts=True)
    histogram_result[mapped_pixel] += count_at_pixel.astype(np.int64)
    return histogram_result


def generate_alignment(histogram, highest_order=10, lowest_order=0, threshold=1_000_000):
    """Generate alignment from high order pixels to those of equal or lower order

    We may initially find healpix pixels at order 10, but after aggregating up to the pixel
    threshold, some final pixels are order 4 or 7. This method provides a map from pixels
    at order 10 to their destination pixel. This may be used as an input into later partitioning
    map reduce steps.

    Args:
        histogram (:obj:`np.array`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        highest_order (int):  the highest healpix order (e.g. 5-10)
        lowest_order (int): the lowest healpix order (e.g. 1-5). specifying a lowest order
            constrains the partitioning to prevent spatially large pixels.
        threshold (int): the maximum number of objects allowed in a single pixel
    Returns:
        one-dimensional numpy array of integer 3-tuples, where the value at each index corresponds
        to the destination pixel at order less than or equal to the `highest_order`.

        The tuple contains three integers:

        - order of the destination pixel
        - pixel number *at the above order*
        - the number of objects in the pixel
    Raises:
        ValueError: if the histogram is the wrong size, or some initial histogram bins
            exceed threshold.
    """
    if len(histogram) != hp.order2npix(highest_order):
        raise ValueError("histogram is not the right size")
    if lowest_order > highest_order:
        raise ValueError("lowest_order should be less than highest_order")
    max_bin = np.amax(histogram)
    if max_bin > threshold:
        raise ValueError(f"single pixel count {max_bin} exceeds threshold {threshold}")

    nested_sums = []
    for i in range(0, highest_order):
        nested_sums.append(empty_histogram(i))
    nested_sums.append(histogram)

    # work backward - from highest order, fill in the sums of lower order pixels
    for read_order in range(highest_order, lowest_order, -1):
        parent_order = read_order - 1
        for index in range(0, len(nested_sums[read_order])):
            parent_pixel = index >> 2
            nested_sums[parent_order][parent_pixel] += nested_sums[read_order][index]

    nested_alignment = []
    for i in range(0, highest_order + 1):
        nested_alignment.append(np.full(hp.order2npix(i), None))

    # work forward - determine if we should map to a lower order pixel, this pixel, or keep looking.
    for read_order in range(lowest_order, highest_order + 1):
        parent_order = read_order - 1
        for index in range(0, len(nested_sums[read_order])):
            parent_alignment = None
            if parent_order >= 0:
                parent_pixel = index >> 2
                parent_alignment = nested_alignment[parent_order][parent_pixel]

            if parent_alignment:
                nested_alignment[read_order][index] = parent_alignment
            elif nested_sums[read_order][index] == 0:
                continue
            elif nested_sums[read_order][index] <= threshold:
                nested_alignment[read_order][index] = (
                    read_order,
                    index,
                    nested_sums[read_order][index],
                )

    return nested_alignment[highest_order]


def generate_destination_pixel_map(histogram, pixel_map):
    """Generate mapping from destination pixel to all the constituent pixels.

    Args:
        histogram (:obj:`np.array`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        pixel_map (:obj:`np.array`): one-dimensional numpy array of integer 3-tuples.
            See :func:`generate_alignment` for more details on this format.
    Returns:
        dictionary that maps the integer 3-tuple of a pixel at destination order to the set of
        indexes in histogram for the pixels at the original healpix order
    """

    # Find all distinct destination pixels
    non_none_elements = pixel_map[pixel_map != np.array(None)]
    unique_pixels = np.unique(non_none_elements)

    # Compute the order from the number of pixels at the level.
    max_order = hp.npix2order(len(histogram))

    result = {}
    for order, pixel, count in unique_pixels:
        # Find all constituent pixels at the histogram's order
        explosion_factor = 4 ** (max_order - int(order))
        start_pixel = int(pixel) * explosion_factor
        end_pixel = (int(pixel) + 1) * explosion_factor

        non_zero_indexes = np.nonzero(histogram[start_pixel:end_pixel])[0] + start_pixel
        result[(order, pixel, count)] = non_zero_indexes.tolist()

    return result


def compute_pixel_map(histogram, highest_order=10, lowest_order=0, threshold=1_000_000):
    # pylint: disable=too-many-locals
    """Generate alignment from high order pixels to those of equal or lower order

    We may initially find healpix pixels at order 10, but after aggregating up to the pixel
    threshold, some final pixels are order 4 or 7. This method provides a map from destination
    healpix pixels at a lower order to the origin pixels at the highest order. This may be used
    as an input into later partitioning map reduce steps.

    Args:
        histogram (:obj:`np.array`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        highest_order (int):  the highest healpix order (e.g. 0-10)
        lowest_order (int): the lowest healpix order (e.g. 1-5). specifying a lowest order
            constrains the partitioning to prevent spatially large pixels.
        threshold (int): the maximum number of objects allowed in a single pixel
    Returns:
        dictionary that maps the HealpixPixel (a pixel at destination order) to a tuple of
        origin pixel information.

        The tuple contains the following:

        - 0 - the total number of rows found in this destination pixel
        - 1 - the set of indexes in histogram for the pixels at the original healpix order.
    Raises:
        ValueError: if the histogram is the wrong size, or some initial histogram bins
            exceed threshold.
    """
    if len(histogram) != hp.order2npix(highest_order):
        raise ValueError("histogram is not the right size")
    if lowest_order > highest_order:
        raise ValueError("lowest_order should be less than highest_order")
    max_bin = np.amax(histogram)
    if max_bin > threshold:
        raise ValueError(f"single pixel count {max_bin} exceeds threshold {threshold}")

    nested_sums = []

    for order in range(0, highest_order):
        explosion_factor = 4 ** (highest_order - order)
        nested_sums.append(histogram.reshape(-1, explosion_factor).sum(axis=1))
    nested_sums.append(histogram)

    ## Determine the lowest order that does not exceed the threshold
    orders_at_threshold = [lowest_order if 0 < k <= threshold else None for k in nested_sums[lowest_order]]
    for order in range(lowest_order + 1, highest_order + 1):
        new_orders_at_threshold = np.array(
            [order if 0 < k <= threshold else None for k in nested_sums[order]]
        )
        parent_alignment = np.repeat(orders_at_threshold, 4, axis=0)
        orders_at_threshold = [
            parent_order if parent_order is not None else new_order
            for parent_order, new_order in zip(parent_alignment, new_orders_at_threshold)
        ]

    ## Zip up the orders and the pixel numbers.
    healpix_pixels = np.array(
        [
            HealpixPixel(order, pixel >> 2 * (highest_order - order)) if order is not None else None
            for order, pixel in zip(orders_at_threshold, np.arange(0, len(orders_at_threshold)))
        ]
    )

    ## Create a map from healpix pixel to origin pixel data
    non_none_elements = healpix_pixels[healpix_pixels != np.array(None)]
    unique_pixels = np.unique(non_none_elements)

    result = {}
    for healpix_pixel in unique_pixels:
        # Find all nonzero constituent pixels at the histogram's order
        explosion_factor = 4 ** (highest_order - healpix_pixel.order)
        start_pixel = healpix_pixel.pixel * explosion_factor
        end_pixel = (healpix_pixel.pixel + 1) * explosion_factor

        non_zero_indexes = np.nonzero(histogram[start_pixel:end_pixel])[0] + start_pixel
        result[healpix_pixel] = (
            nested_sums[healpix_pixel.order][healpix_pixel.pixel],
            non_zero_indexes.tolist(),
        )
    return result


def generate_constant_pixel_map(histogram, constant_healpix_order):
    """Special case of creating a destination pixel map where you want to
    preserve some constant healpix order across the sky.

    NB:
        - this method filters out pixels with no counts
        - no upper thresholds are applied, and single pixel may contain many rows

    Args:
        histogram (:obj:`np.array`): one-dimensional numpy array of long integers where the
            value at each index corresponds to the number of objects found at the healpix pixel.
        constant_healpix_order (int):  the desired healpix order (e.g. 0-10)
    Returns:
        dictionary that maps non-empty bins as HealpixPixel to a tuple of origin pixel
        information.

        The tuple contains the following:

        - 0 - the total number of rows found in this destination pixel, same as the origin bin
        - 1 - the set of indexes in histogram for the pixels at the original healpix
          order, which will be a list containing only the origin pixel.
    Raises:
        ValueError: if the histogram is the wrong size
    """
    if len(histogram) != hp.order2npix(constant_healpix_order):
        raise ValueError("histogram is not the right size")

    non_zero_indexes = np.nonzero(histogram)[0]
    healpix_pixels = [HealpixPixel(constant_healpix_order, pixel) for pixel in non_zero_indexes]

    value_list = [(histogram[pixel], [pixel]) for pixel in non_zero_indexes]

    return dict(zip(healpix_pixels, value_list))
