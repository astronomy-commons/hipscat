from enum import Enum


class CatalogType(str, Enum):
    OBJECT = "object"
    SOURCE = "source"
    ASSOCIATION = "association"
    INDEX = "index"
    MARGIN = "margin"
