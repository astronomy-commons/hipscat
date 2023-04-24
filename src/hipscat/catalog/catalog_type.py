from enum import Enum


class CatalogType(str, Enum):
    """Enum for possible types of catalog"""

    OBJECT = "object"
    SOURCE = "source"
    ASSOCIATION = "association"
    INDEX = "index"
    MARGIN = "margin"
