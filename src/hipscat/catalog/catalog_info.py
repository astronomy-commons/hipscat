from dataclasses import dataclass

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


@dataclass
class CatalogInfo(BaseCatalogInfo):
    epoch: str = "J2000"
    ra_column: str = "ra"
    dec_column: str = "dec"
