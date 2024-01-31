from __future__ import annotations

from enum import Enum
from typing import List, Tuple

import numpy as np


class ValidatorsErrors(str, Enum):
    """Error messages for the coordinate validators"""

    INVALID_DEC = "declination must be in the -90.0 to 90.0 degree range"
    INVALID_RADIUS = "cone radius must be positive"
    INVALID_NUM_VERTICES = "polygon must contain a minimum of 3 vertices"
    DUPLICATE_VERTICES = "polygon has duplicated vertices"
    DEGENERATE_POLYGON = "polygon is degenerate"


def validate_radius(radius: float):
    """Validates that a cone search radius is positive

    Arguments:
        radius (float): The cone radius, in degrees

    Raises:
        ValueError if radius is non-positive
    """
    if radius <= 0:
        raise ValueError(ValidatorsErrors.INVALID_RADIUS.value)


def validate_declination_values(dec: float | List[float]):
    """Validates that declination values are in the [-90,90] degree range

    Arguments:
        dec (float | List[float]): The declination values to be validated

    Raises:
        ValueError if declination values are not in the [-90,90] degree range
    """
    dec_values = np.array(dec)
    lower_bound, upper_bound = -90.0, 90.0
    if not np.all((dec_values >= lower_bound) & (dec_values <= upper_bound)):
        raise ValueError(ValidatorsErrors.INVALID_DEC.value)


def validate_polygon(vertices: np.ndarray):
    """Checks if the polygon contain a minimum of three vertices, that they are
    unique and that the polygon does not fall on a great circle.

    Arguments:
        vertices (np.ndarray): The polygon vertices, in cartesian coordinates

    Raises:
        ValueError exception if the polygon is invalid.
    """
    if len(vertices) < 3:
        raise ValueError(ValidatorsErrors.INVALID_NUM_VERTICES.value)
    if len(vertices) != len(np.unique(vertices, axis=0)):
        raise ValueError(ValidatorsErrors.DUPLICATE_VERTICES.value)
    if is_polygon_degenerate(vertices):
        raise ValueError(ValidatorsErrors.DEGENERATE_POLYGON.value)


def is_polygon_degenerate(vertices: np.ndarray) -> bool:
    """Checks if all the vertices of the polygon are contained in a same plane.
    If the plane intersects the center of the sphere, the polygon is degenerate.

    Arguments:
        vertices (np.ndarray): The polygon vertices, in cartesian coordinates

    Returns:
        A boolean, which is True if the polygon is degenerate, i.e. if it falls
        on a great circle, False otherwise.
    """
    # Calculate the normal vector of the plane using three of the vertices
    normal_vector = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])

    # Check if the other vertices lie on the same plane
    for vertex in vertices[3:]:
        dot_product = np.dot(normal_vector, vertex - vertices[0])
        if not np.isclose(dot_product, 0):
            return False

    # Check if the plane intersects the sphere's center. If it does,
    # the polygon is degenerate and therefore, invalid.
    center_distance = np.dot(normal_vector, vertices[0])
    return bool(np.isclose(center_distance, 0))


def validate_box_search(ra: Tuple[float, float] | None, dec: Tuple[float, float] | None):
    """Checks if ra and dec values are valid for the box search.
    They must be pairs (of minimum and maximum value, in degrees).

    Arguments:
        ra (Tuple[float, float]): Right ascension range, in degrees
        dec (Tuple[float, float]): Declination range, in degrees

    Raises:
        ValueError, if declination values are out of range [-90,90]
        or if no range was provided.
    """
    values_provided = False
    if ra is not None and len(ra) == 2:
        values_provided = True
    if dec is not None and len(dec) == 2:
        validate_declination_values(list(dec))
        values_provided = True
    if not values_provided:
        raise ValueError("Provide ra or dec range")
