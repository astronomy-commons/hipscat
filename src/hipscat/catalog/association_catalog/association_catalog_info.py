from dataclasses import dataclass

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


@dataclass
class AssociationCatalogInfo(BaseCatalogInfo):
    """Catalog Info for a HiPSCat Association Catalog"""

    primary_catalog: str = None
    """Catalog name for the primary (left) side of association"""

    primary_column: str = None
    """Column name in the primary (left) side of join"""

    join_catalog: str = None
    """Catalog name for the joining (right) side of association"""

    join_column: str = None
    """Column name in the joining (right) side of join"""

    required_fields = BaseCatalogInfo.required_fields + [
        "primary_catalog",
        "join_catalog",
    ]

    DEFAULT_TYPE = CatalogType.ASSOCIATION
    REQUIRED_TYPE = CatalogType.ASSOCIATION
