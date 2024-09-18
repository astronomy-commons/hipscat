"""Catalog Info for a HATS Index table"""

from dataclasses import dataclass, field
from typing import List

from hats.catalog.catalog_type import CatalogType
from hats.catalog.dataset.base_catalog_info import BaseCatalogInfo


@dataclass
class IndexCatalogInfo(BaseCatalogInfo):
    """Catalog Info for a HATS Index table"""

    primary_catalog: str = None
    """Reference to object or source catalog"""

    indexing_column: str = None
    """Column that we provide an index over"""

    extra_columns: List[str] = field(default_factory=list)
    """Any additional payload columns included in index"""

    required_fields = BaseCatalogInfo.required_fields + [
        "primary_catalog",
        "indexing_column",
    ]

    DEFAULT_TYPE = CatalogType.INDEX
    REQUIRED_TYPE = CatalogType.INDEX
