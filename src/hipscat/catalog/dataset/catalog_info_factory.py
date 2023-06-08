import dataclasses

from hipscat.catalog.association_catalog.association_catalog_info import \
    AssociationCatalogInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.catalog.index.index_catalog_info import IndexCatalogInfo
from hipscat.catalog.margin_cache.margin_cache_catalog_info import \
    MarginCacheCatalogInfo
from hipscat.catalog.source_catalog.source_catalog_info import \
    SourceCatalogInfo
from hipscat.io import FilePointer, file_io, paths


def create_catalog_info(
    keywords: dict, catalog_type: str = None
) -> BaseCatalogInfo:
    """Generate a typed catalog info object from the type specified explicitly or 
    using ``catalog_type`` keyword."""

    if not catalog_type:
        if "catalog_type" not in keywords.keys():
            raise ValueError("catalog type is required to create catalog info object")
        catalog_type = keywords["catalog_type"]

    if catalog_type not in CatalogType.all_types():
        raise ValueError(f"Unknown catalog type: {catalog_type}")
    
    ci_class = None

    if catalog_type == CatalogType.OBJECT:
        ci_class = CatalogInfo
    elif catalog_type == CatalogType.SOURCE:
        ci_class = SourceCatalogInfo
    elif catalog_type == CatalogType.ASSOCIATION:
        ci_class = AssociationCatalogInfo
    elif catalog_type == CatalogType.INDEX:
        ci_class = IndexCatalogInfo
    elif catalog_type == CatalogType.MARGIN:
        ci_class = MarginCacheCatalogInfo
    else:
        raise NotImplementedError(f"Unhandled catalog type: {catalog_type}")

    catalog_info_keywords = {}
    for field in dataclasses.fields(ci_class):
        if field.name in keywords:
            catalog_info_keywords[field.name] = keywords[field.name]
    return ci_class(**catalog_info_keywords)

def from_catalog_dir(catalog_base_dir: FilePointer):
    """Generate a typed catalog info object from the type specified in the 
    catalog info file."""
    if file_io.is_regular_file(catalog_base_dir):
        ## This might be the catalog_info.json file - try anyway
        metadata_keywords = file_io.load_json_file(catalog_base_dir)
    else:
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        metadata_keywords = file_io.load_json_file(catalog_info_file)
    return create_catalog_info(metadata_keywords)
