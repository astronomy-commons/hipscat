from __future__ import annotations

from typing import Type

from hipscat import io
from hipscat.catalog import AssociationCatalog, Catalog, CatalogType, Dataset, MarginCatalog
from hipscat.catalog.dataset import BaseCatalogInfo
from hipscat.catalog.index.index_catalog import IndexCatalog

CATALOG_TYPE_TO_CLASS = {
    CatalogType.OBJECT: Catalog,
    CatalogType.SOURCE: Catalog,
    CatalogType.ASSOCIATION: AssociationCatalog,
    CatalogType.INDEX: IndexCatalog,
    CatalogType.MARGIN: MarginCatalog,
}


def read_from_hipscat(catalog_path: str, catalog_type: CatalogType | None = None) -> Dataset:
    """Reads a HiPSCat Catalog from a HiPSCat directory

    Args:
        catalog_path (str): path to the root directory of the catalog
        catalog_type (CatalogType): Default `None`. By default, the type of the catalog is loaded
            from the catalog info and the corresponding object type is returned. Python's type hints
            cannot allow a return type specified by a loaded value, so to use the correct return
            type for type checking, the type of the catalog can be specified here. Use by specifying
            the hipscat class for that catalog.

    Returns:
        The initialized catalog object
    """
    catalog_type_to_use = (
        _read_dataset_class_from_metadata(catalog_path) if catalog_type is None else catalog_type
    )
    loader = _get_loader_from_catalog_type(catalog_type_to_use)
    return loader.read_from_hipscat(catalog_path)


def _read_dataset_class_from_metadata(catalog_base_path: str) -> CatalogType:
    catalog_base_dir = io.file_io.get_upath(catalog_base_path)
    catalog_info_path = io.paths.get_catalog_info_pointer(catalog_base_dir)
    catalog_info = BaseCatalogInfo.read_from_metadata_file(catalog_info_path)
    return catalog_info.catalog_type


def _get_loader_from_catalog_type(catalog_type: CatalogType) -> Type[Dataset]:
    if catalog_type not in CATALOG_TYPE_TO_CLASS:
        raise NotImplementedError(f"Cannot load catalog of type {catalog_type}")
    return CATALOG_TYPE_TO_CLASS[catalog_type]
