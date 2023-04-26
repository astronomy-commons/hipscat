from dataclasses import dataclass

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


@dataclass
class AssociationCatalogInfo(BaseCatalogInfo):
    """Catalog Info for a HiPSCat Association Catalog"""

    primary_catalog: str = None
    primary_column: str = None
    join_catalog: str = None
    join_column: str = None

    required_fields = BaseCatalogInfo.required_fields + [
        "primary_catalog",
        "join_catalog",
    ]
