"""Catalog Info for a HiPSCat Margin cache table"""

from dataclasses import dataclass

from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType


@dataclass
class MarginCacheCatalogInfo(CatalogInfo):
    """Catalog Info for a HiPSCat Margin Cache table"""

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
