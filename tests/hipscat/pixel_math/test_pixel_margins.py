"""Tests of pixel margin utility functions"""

import numpy as np
import numpy.testing as npt
import pytest

import hipscat.pixel_math as pm


def test_get_margin():
    """Check that the code works in the standard case."""
    margins = pm.get_margin(2, 2, 2)

    expected = np.array(
        [
            1141,
            1143,
            1149,
            1151,
            1237,
            128,
            129,
            132,
            133,
            144,
            48,
            50,
            56,
            58,
            26,
            10,
            11,
            14,
            15,
            1119,
        ]
    )

    assert len(margins) == 20

    npt.assert_array_equal(margins, expected)


def test_zero_dk():
    """Check that the code fails when trying to find margins at same order as the pixel."""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin(2, 2, 0)

    assert str(value_error.value) == "dk must be greater than order"


def test_negative_dk():
    """Check that the code fails when trying to find margins at a higher order than the pixel."""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin(2, 2, -1)

    assert str(value_error.value) == "dk must be greater than order"


def test_polar_edge():
    """Check that the code works when trying to find margins around the north pole."""
    margins = pm.get_margin(2, 5, 2)

    expected = np.array(
        [
            69,
            71,
            77,
            79,
            101,
            112,
            113,
            116,
            117,
            442,
            426,
            427,
            430,
            431,
            1530,
            1531,
            1534,
            1535,
            1519,
        ]
    )

    assert len(margins) == 19

    npt.assert_array_equal(margins, expected)


def test_polar_edge_south():
    """Check that the code works when trying to find margins around the south pole."""
    margins = pm.get_margin(1, 35, 2)

    expected = np.array(
        [
            549,
            551,
            557,
            559,
            261,
            272,
            273,
            276,
            277,
            0,
            352,
            354,
            360,
            362,
            330,
            538,
            539,
            542,
            543,
            527,
        ]
    )
    assert len(margins) == 20

    npt.assert_array_equal(margins, expected)


def test_edge_negative_value():
    """Check to make sure get_edge fails when passed a negative edge value."""
    with pytest.raises(ValueError) as value_error:
        pm.get_edge(2, 5, -1)

    assert (
        str(value_error.value)
        == "edge can only be values between 0 and 7 (see docstring)"
    )


def test_edge_greater_than_7():
    """Check to make sure get_edge fails when passed an edge value greater than 7."""
    with pytest.raises(ValueError) as value_error:
        pm.get_edge(2, 5, 8)

    assert (
        str(value_error.value)
        == "edge can only be values between 0 and 7 (see docstring)"
    )

def test_get_margin_scale():
    """Check to make sure that get_margin_scale works as expected."""
    scale = pm.get_margin_scale(3, 0.1)
    
    expected = 1.0274748806654526

    assert scale == expected

def test_get_margin_scale_k_zero():
    """Make sure get_margin_scale works when k == 0"""
    scale = pm.get_margin_scale(0, 0.1)

    expected = 1.0034139979085752

    assert scale == expected

def test_get_margin_scale_k_high():
    """Make sure get_margin_scale works when k is a high order"""
    scale = pm.get_margin_scale(64, 0.1)

    expected = 9.89841281541636e+32

    assert scale == expected

def test_negative_margin_threshold():
    """Make sure that get_marin_scale raises a value error when threshold is < 0.0"""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin_scale(3, -0.1)

    assert(
        str(value_error.value)
        == "margin_threshold must be greater than 0."
    )

def test_negative_margin_threshold():
    """Make sure that get_marin_scale raises a value error when threshold is == 0.0"""
    with pytest.raises(ValueError) as value_error:
        pm.get_margin_scale(3, 0.0)

    assert(
        str(value_error.value)
        == "margin_threshold must be greater than 0."
    )