from __future__ import annotations

from dataclasses import dataclass

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


@dataclass
class AssociationCatalogInfo(BaseCatalogInfo):
    """Catalog Info for a HiPSCat Association Catalog"""

    primary_catalog: str | None = None
    """Catalog name for the primary (left) side of association"""

    primary_column: str | None = None
    """Column name in the primary (left) side of join"""

    primary_column_association: str | None = None
    """Column name in the association table that matches the primary (left) side of join"""

    join_catalog: str | None = None
    """Catalog name for the joining (right) side of association"""

    join_column: str | None = None
    """Column name in the joining (right) side of join"""

    join_column_association: str | None = None
    """Column name in the association table that matches the joining (right) side of join"""

    contains_leaf_files: bool = False
    """Whether or not the association catalog contains leaf parquet files"""

    required_fields = BaseCatalogInfo.required_fields + [
        "primary_catalog",
        "primary_column",
        "join_catalog",
        "join_column",
        "contains_leaf_files",
    ]

    DEFAULT_TYPE = CatalogType.ASSOCIATION
    REQUIRED_TYPE = CatalogType.ASSOCIATION
