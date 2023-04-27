from enum import Enum


class PixelAlignmentType(str, Enum):

    INNER = "inner"
    OUTER = "outer"
    LEFT = "left"
    RIGHT = "right"
