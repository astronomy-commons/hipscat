from enum import Enum


class PixelAlignmentType(Enum, str):

    INNER = "inner"
    OUTER = "outer"
    LEFT = "left"
    RIGHT = "right"
