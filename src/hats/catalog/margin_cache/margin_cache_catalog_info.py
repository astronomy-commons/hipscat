"""Catalog Info for a HATS Margin cache table"""

from dataclasses import dataclass

from hats.catalog.catalog_info import CatalogInfo
from hats.catalog.catalog_type import CatalogType


@dataclass
class MarginCacheCatalogInfo(CatalogInfo):
    """Catalog Info for a HATS Margin Cache table"""

    primary_catalog: str = None
    """Reference to object or source catalog"""

    margin_threshold: float = None
    """Threshold of the pixel boundary, expressed in arcseconds."""

    required_fields = CatalogInfo.required_fields + [
        "primary_catalog",
        "margin_threshold",
    ]

    DEFAULT_TYPE = CatalogType.MARGIN
    REQUIRED_TYPE = CatalogType.MARGIN
