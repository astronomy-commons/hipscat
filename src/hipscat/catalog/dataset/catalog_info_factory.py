import dataclasses

from hipscat.catalog.association_catalog.association_catalog_info import (
    AssociationCatalogInfo,
)
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


def create_catalog_info(
    keywords: dict, catalog_type: str = "object"
) -> BaseCatalogInfo:
    """Generate a typed catalog info object from the type specified explicitly or using ``catalog_type`` keyword."""

    if not catalog_type:
        if "catalog_type" not in keywords.keys():
            raise ValueError("catalog type is required to create catalog info object")
        catalog_type = keywords["catalog_type"]

    ## TODO - use list on object;
    CATALOG_TYPES = [t.value for t in CatalogType]

    if catalog_type not in CATALOG_TYPES:
        raise ValueError(f"Unknown catalog type: {catalog_type}")

    ci_class = None

    if catalog_type == CatalogType.OBJECT or catalog_type == CatalogType.SOURCE:
        ci_class = CatalogInfo
    elif catalog_type == CatalogType.ASSOCIATION:
        ci_class = AssociationCatalogInfo

    catalog_info_keywords = {}
    for field in dataclasses.fields(ci_class):
        if field.name in keywords:
            catalog_info_keywords[field.name] = keywords[field.name]
    return ci_class(**catalog_info_keywords)
