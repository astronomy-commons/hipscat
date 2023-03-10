"""Utilities for performing fun math on healpix pixels"""

from .partition_stats import (
    empty_histogram,
    generate_alignment,
    generate_destination_pixel_map,
    generate_histogram,
)

from .pixel_margins import get_edge, get_margin
