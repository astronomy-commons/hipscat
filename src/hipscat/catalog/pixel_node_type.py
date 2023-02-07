from enum import Enum


class PixelNodeType(Enum):
    """Node type classification."""

    ROOT = 0
    INNER = 1
    LEAF = 2
