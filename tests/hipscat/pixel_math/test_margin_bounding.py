"""Tests of margin bounding utility functions"""

import numpy as np
import numpy.testing as npt
import pytest
from astropy.coordinates import SkyCoord
from regions import PixCoord

import hipscat.pixel_math as pm


def test_get_margin_scale():
    """Check to make sure that get_margin_scale works as expected."""
    scale = pm.get_margin_scale(3, 0.1)

    expected = 1.0272887122119063

    assert scale == expected


def test_get_margin_scale_k_zero():
    """Make sure get_margin_scale works when k == 0"""
    scale = pm.get_margin_scale(0, 0.1)

    expected = 1.0034110890264882

    assert scale == expected


def test_get_margin_scale_k_high():
    """Make sure get_margin_scale works when k is a high order"""
    scale = pm.get_margin_scale(64, 0.1)

    expected = 6.292348628426864e16

    assert scale == expected


def test_negative_margin_threshold():
    """Make sure that get_marin_scale raises a value error when threshold is < 0.0"""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin_scale(3, -0.1)

    assert str(value_error.value) == "margin_threshold must be greater than 0."


def test_zero_margin_threshold():
    """Make sure that get_marin_scale raises a value error when threshold is == 0.0"""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin_scale(3, 0.0)

    assert str(value_error.value) == "margin_threshold must be greater than 0."


def test_get_margin_bounds_and_wcs():
    """Make sure get_margin_bounds_and wcs works as expected."""
    # far out point, expect False
    test_ra1 = 42.0
    test_dec1 = 1.0

    # middle of our healpixel, expect True
    test_ra2 = 56.25
    test_dec2 = 14.49584495

    # actual point from Norder3/Npix4 of my
    # gaia test catalog, expect True
    # if k = 3 and pix = 4
    test_ra3 = 50.61225197
    test_dec3 = 14.4767556

    test_ra = np.array([test_ra1, test_ra2, test_ra3])
    test_dec = np.array([test_dec1, test_dec2, test_dec3])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    scale = pm.get_margin_scale(3, 0.1)
    polygon, wcs_margin = pm.get_margin_bounds_and_wcs(3, 4, scale)[0]

    assert polygon.area == pytest.approx(756822775.0000424, 0.001)

    coord_x, coord_y = wcs_margin.world_to_pixel(test_sc)
    expected_pixel_coord = PixCoord(coord_x, coord_y)
    expected_contains_checks = np.array([False, True, True])

    contains_checks = polygon.contains(expected_pixel_coord)

    npt.assert_array_equal(contains_checks, expected_contains_checks)


def get_checks_for_bounds(bounds, test_sky_coords):
    """Helper method for getting the check flags for
    some boundaries and sky coordinates to check."""
    vals = []
    for polygon, margin in bounds:
        coord_x, coord_y = margin.world_to_pixel(test_sky_coords)

        vals.append(polygon.contains(PixCoord(coord_x, coord_y)))

    return np.array(vals).any(axis=0)


def test_get_margin_bounds_and_wcs_low_order():
    """Make sure get_margin_bounds_and wcs works as expected."""
    # far out point, expect False
    test_ra1 = 90.0
    test_dec1 = -2.0

    # middle of our healpixel, expect True
    test_ra2 = -100.0
    test_dec2 = -45.0

    test_ra = np.array([test_ra1, test_ra2])
    test_dec = np.array([test_dec1, test_dec2])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    scale = pm.get_margin_scale(0, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(0, 5, scale)

    assert len(bounds) == 16

    expected = np.array([True, False])

    npt.assert_array_equal(get_checks_for_bounds(bounds, test_sc), expected)


def test_get_margin_bounds_and_wcs_north_pole():
    """Make sure get_margin_bounds_and_wcs works at pixels along the north polar region"""
    scale = pm.get_margin_scale(1, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(1, 7, scale, step=100)

    assert len(bounds) == 4

    test_ra = np.array([50, 100.0, 130.0, 130.0, 100.0])
    test_dec = np.array([-60.0, 89.9, 65.0, 85.0, 50.0])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    expected = np.array([False, True, True, True, False])

    npt.assert_array_equal(get_checks_for_bounds(bounds, test_sc), expected)


def test_get_margin_bounds_and_wcs_south_pole():
    """Make sure get_margin_bounds_and_wcs works at pixels along the south polar region"""
    scale = pm.get_margin_scale(1, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(1, 36, scale)

    assert len(bounds) == 4

    test_ra = np.array([50, 120.0, 108.0, 150.0, 100.0, 104.0])
    test_dec = np.array([-60.0, -70.0, -66.2, -70.0, -90.0, -80])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    expected = np.array([False, True, True, True, False, True])

    npt.assert_array_equal(get_checks_for_bounds(bounds, test_sc), expected)


def test_get_margin_bounds_and_wcs_ra_rollover():
    """Make sure get_margin_bounds_and_wcs works at the rollover point for right ascension"""
    scale = pm.get_margin_scale(1, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(1, 27, scale)

    assert len(bounds) == 4

    test_ra = np.array([180.0, 0.0, -157.5, 120.0, 157.5])
    test_dec = np.array([20.0, 0.0, 19.4, 20.0, 19.4])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    expected = np.array([True, False, True, False, True])

    npt.assert_array_equal(get_checks_for_bounds(bounds, test_sc), expected)


def test_get_margin_bounds_and_wcs_origin():
    """Make sure get_margin_bounds_and_wcs works at the origin of ra and dec."""
    scale = pm.get_margin_scale(0, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(0, 4, scale)

    assert len(bounds) == 16

    test_ra = np.array([180.0, -20.0])
    test_dec = np.array([20.0, -10.0])

    test_sc = SkyCoord(test_ra, test_dec, unit="deg")

    expected = np.array([False, True])

    npt.assert_array_equal(get_checks_for_bounds(bounds, test_sc), expected)


def test_check_margin_bounds():
    """Make sure check_margin_bounds works properly"""
    scale = pm.get_margin_scale(3, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(3, 4, scale)

    test_ra = np.array([42.4704538, 56.25, 50.61225197])
    test_dec = np.array([1.4593925, 14.49584495, 14.4767556])

    checks = pm.check_margin_bounds(test_ra, test_dec, bounds)

    expected = np.array([False, True, True])

    npt.assert_array_equal(checks, expected)


def test_check_margin_bounds_multi_poly():
    """Make sure check_margin_bounds works when poly_and_wcs has multiple entries"""
    scale = pm.get_margin_scale(1, 0.1)
    bounds = pm.get_margin_bounds_and_wcs(1, 4, scale)

    test_ra = np.array([42.4704538, 120.0, 135.0])
    test_dec = np.array([1.4593925, 25.0, 19.92530172])

    checks = pm.check_margin_bounds(test_ra, test_dec, bounds)

    expected = np.array([False, True, True])

    npt.assert_array_equal(checks, expected)


def test_check_polar_margin_bounds_north():
    """Make sure check_polar_margin_bounds works at the north pole"""
    order = 0
    pix = 1
    margin_order = 2

    test_ra = np.array([89, -179, -45])
    test_dec = np.array([89.9, 89.9, 85.0])

    vals = pm.check_polar_margin_bounds(test_ra, test_dec, order, pix, margin_order, 0.1)

    expected = np.array([True, True, False])

    npt.assert_array_equal(vals, expected)


def test_check_polar_margin_bounds_south():
    """Make sure check_polar_margin_bounds works at the south pole"""
    order = 0
    pix = 9
    margin_order = 2

    test_ra = np.array([89, -179, -45])
    test_dec = np.array([-89.9, -89.9, -85.0])

    vals = pm.check_polar_margin_bounds(test_ra, test_dec, order, pix, margin_order, 0.1)

    expected = np.array([True, True, False])

    npt.assert_array_equal(vals, expected)


def test_check_polar_margin_bounds_non_pole():
    """Make sure check_polar_margin_bounds raises a ValueError when pix isn't polar"""
    order = 0
    pix = 7
    margin_order = 2

    test_ra = np.array([89, -179, -45])
    test_dec = np.array([-89.9, -89.9, -85.0])

    with pytest.raises(ValueError) as value_error:
        pm.check_polar_margin_bounds(test_ra, test_dec, order, pix, margin_order, 0.1)

    assert str(value_error.value) == "provided healpixel must be polar"
