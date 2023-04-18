"""Tests of histogram calculations"""

import healpy as hp
import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

import hipscat.pixel_math as hist
from hipscat.pixel_math.healpix_pixel import HealpixPixel


def test_small_sky_same_pixel():
    """Test partitioning two objects into the same large bucket"""

    data = pd.DataFrame(
        data=[[700, 282.5, -58.5], [701, 299.5, -48.5]],
        columns=["id", "ra", "dec"],
    )

    result = hist.generate_histogram(
        data=data,
        highest_order=0,
    )

    assert len(result) == 12

    expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
    npt.assert_array_equal(result, expected)
    assert (result == expected).all()


def test_column_names_error():
    """Test with non-default column names (without specifying column names)"""

    data = pd.DataFrame(
        data=[[700, 282.5, -58.5], [701, 299.5, -48.5]],
        columns=["id", "ra_mean", "dec_mean"],
    )

    with pytest.raises(ValueError) as error:
        hist.generate_histogram(
            data=data,
            highest_order=0,
        )
        assert "Invalid column names" in error.value


def test_column_names():
    """Test with non-default column names"""
    data = pd.DataFrame(
        data=[[700, 282.5, -58.5], [701, 299.5, -48.5]],
        columns=["id", "ra_mean", "dec_mean"],
    )

    result = hist.generate_histogram(
        data=data,
        highest_order=0,
        ra_column="ra_mean",
        dec_column="dec_mean",
    )

    assert len(result) == 12

    expected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
    npt.assert_array_equal(result, expected)
    assert (result == expected).all()


def test_alignment_wrong_size():
    """Check that the method raises error when the input histogram is not the expected size."""
    initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 131])
    with pytest.raises(ValueError) as error:
        hist.generate_alignment(initial_histogram, 0, 250)
        assert "histogram is not the right size" == error.value


def test_alignment_exceeds_threshold_order0():
    """Check that the method raises error when some pixel exceeds the threshold."""
    initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])
    with pytest.raises(ValueError) as error:
        hist.generate_alignment(initial_histogram, 0, 20)
        assert "exceeds threshold" in error.value


def test_alignment_exceeds_threshold_order2():
    """Check that the method raises error when some pixel exceeds the threshold."""
    initial_histogram = hist.empty_histogram(2)
    filled_pixels = [4, 11, 14, 13, 5, 7, 8, 9, 11, 23, 4, 4, 17, 0, 1, 0]
    initial_histogram[176:] = filled_pixels[:]
    with pytest.raises(ValueError) as error:
        hist.generate_alignment(initial_histogram, 2, 20)
        assert "exceeds threshold" in error.value


def test_alignment_small_sky_order0():
    """Create alignment from small sky's distribution at order 0"""
    initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])
    result = hist.generate_alignment(initial_histogram, 0, 250)

    expected = np.full(12, None)
    expected[11] = (0, 11, 131)

    npt.assert_array_equal(result, expected)


def test_alignment_small_sky_order1():
    """Create alignment from small sky's distribution at order 1"""
    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [42, 29, 42, 18]
    initial_histogram[44:] = filled_pixels[:]
    result = hist.generate_alignment(initial_histogram, 1, 250)

    expected = np.full(48, None)
    expected[44:] = [(0, 11, 131), (0, 11, 131), (0, 11, 131), (0, 11, 131)]

    npt.assert_array_equal(result, expected)


def test_alignment_small_sky_order2():
    """Create alignment from small sky's distribution at order 2"""
    initial_histogram = hist.empty_histogram(2)
    filled_pixels = [4, 11, 14, 13, 5, 7, 8, 9, 11, 23, 4, 4, 17, 0, 1, 0]
    initial_histogram[176:] = filled_pixels[:]
    result = hist.generate_alignment(initial_histogram, 2, 250)

    expected = np.full(hp.order2npix(2), None)
    tuples = [
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
        (0, 11, 131),
    ]
    expected[176:192] = tuples

    npt.assert_array_equal(result, expected)


def test_alignment_even_sky():
    """Create alignment from an even distribution at order 8"""
    initial_histogram = np.full(hp.order2npix(8), 10)
    result = hist.generate_alignment(initial_histogram, 8, 1_000)
    # everything maps to order 5, given the density
    for mapping in result:
        assert mapping[0] == 5


def test_destination_pixel_map_order1():
    """Create destination pixel map for small sky at order 1"""

    alignment = np.full(48, None)
    alignment[44:] = [(0, 11, 131), (0, 11, 131), (0, 11, 131), (0, 11, 131)]

    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]

    expected = {tuple([0, 11, 131]): [44, 45, 46]}

    result = hist.generate_destination_pixel_map(initial_histogram, alignment)

    npt.assert_array_equal(result, expected)


def test_compute_pixel_map_order1():
    """Create destination pixel map for small sky at order 1"""

    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]

    expected = {HealpixPixel(0, 11): (131, [44, 45, 46])}

    result = hist.compute_pixel_map(initial_histogram, highest_order=1, threshold=150)

    npt.assert_array_equal(result, expected)

    expected = {
        HealpixPixel(1, 44): (51, [44]),
        HealpixPixel(1, 45): (29, [45]),
        HealpixPixel(1, 46): (51, [46]),
    }

    result = hist.compute_pixel_map(initial_histogram, highest_order=1, threshold=100)

    npt.assert_array_equal(result, expected)


def test_compute_pixel_map_invalid_inputs():
    """Create destination pixel map for small sky at order 1"""

    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]

    ## Order doesn't match histogram length
    with pytest.raises(ValueError) as length_error:
        hist.compute_pixel_map(initial_histogram, highest_order=2, threshold=150)
        assert "histogram is not the right size" in length_error.value

    ## Some bins exceed threshold
    with pytest.raises(ValueError) as threshold_error:
        hist.compute_pixel_map(initial_histogram, highest_order=1, threshold=30)
        assert "exceeds threshold" in threshold_error.value


def test_generate_constant_pixel_map():
    """Create constant pixel map for small sky data"""

    initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])
    expected = {HealpixPixel(0, 11): (131, [11])}

    result = hist.generate_constant_pixel_map(
        initial_histogram, constant_healpix_order=0
    )
    npt.assert_array_equal(result, expected)

    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]
    expected = {
        HealpixPixel(1, 44): (51, [44]),
        HealpixPixel(1, 45): (29, [45]),
        HealpixPixel(1, 46): (51, [46]),
    }

    result = hist.generate_constant_pixel_map(
        initial_histogram, constant_healpix_order=1
    )

    npt.assert_array_equal(result, expected)


def test_generate_constant_pixel_map_invalid_inputs():
    """Create destination pixel map for small sky at order 1"""

    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]

    ## Order doesn't match histogram length
    with pytest.raises(ValueError) as length_error:
        hist.generate_constant_pixel_map(initial_histogram, constant_healpix_order=2)
        assert "histogram is not the right size" in length_error.value
