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


def read_from_hipscat(
    catalog_path: str,
    catalog_type: Type[Dataset] | None = None,
    storage_options: dict | None = None,
) -> Dataset:
    """Reads a HiPSCat Catalog from a HiPSCat directory

    Args:
        catalog_path (str): path to the root directory of the catalog
        catalog_type (Type[Dataset]): Default `None`. By default, the type of the catalog is loaded
            from the catalog info and the corresponding object type is returned. Python's type hints
            cannot allow a return type specified by a loaded value, so to use the correct return
            type for type checking, the type of the catalog can be specified here. Use by specifying
            the lsdb class for that catalog.
        storage_options (dict): dictionary that contains abstract filesystem credentials

    Returns:
        The initialized catalog object
    """
    catalog_type_to_use = _get_dataset_class_from_catalog_info(catalog_path, storage_options=storage_options)
    if catalog_type is not None:
        catalog_type_to_use = catalog_type
    return catalog_type_to_use.read_from_hipscat(catalog_path)


def _get_dataset_class_from_catalog_info(
    catalog_base_path: str, storage_options: dict | None = None
) -> Type[Dataset]:
    catalog_base_dir = io.file_io.get_file_pointer_from_path(catalog_base_path)
    catalog_info_path = io.paths.get_catalog_info_pointer(catalog_base_dir)
    catalog_info = BaseCatalogInfo.read_from_metadata_file(catalog_info_path, storage_options=storage_options)
    catalog_type = catalog_info.catalog_type
    if catalog_type not in CATALOG_TYPE_TO_CLASS:
        raise NotImplementedError(f"Cannot load catalog of type {catalog_type}")
    return CATALOG_TYPE_TO_CLASS[catalog_type]
