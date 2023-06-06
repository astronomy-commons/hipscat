from dataclasses import dataclass

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


@dataclass
class CatalogInfo(BaseCatalogInfo):
    """Catalog Info for a HEALPix Hive partitioned Catalog"""

    epoch: str = "J2000"
    ra_column: str = "ra"
    dec_column: str = "dec"

    required_fields = BaseCatalogInfo.required_fields + [
        "epoch",
        "ra_column",
        "dec_column",
    ]

    DEFAULT_TYPE = CatalogType.OBJECT
