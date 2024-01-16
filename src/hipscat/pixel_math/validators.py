from __future__ import annotations

from enum import Enum
from typing import List

import numpy as np


class ValidatorsErrors(str, Enum):
    """Error messages for the coordinate validators"""
    INVALID_DEC = "declination must be in the -90.0 to 90.0 degree range"


def validate_declination_values(dec: float | List[float]):
    """Validates that declination values are in the [-90,90] degree range

    Arguments:
        dec (float | List[float]): The declination values to be validated

    Raises:
        ValueError if declination values are not in the [-90,90] degree range
    """
    dec_values = np.array(dec)
    lower_bound, upper_bound = -90., 90.
    if not np.all((dec_values >= lower_bound) & (dec_values <= upper_bound)):
        raise ValueError(ValidatorsErrors.INVALID_DEC.value)
