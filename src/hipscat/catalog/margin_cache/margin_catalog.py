from __future__ import annotations

from typing_extensions import TypeAlias

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.healpix_dataset.healpix_dataset import HealpixDataset, PixelInputTypes
from hipscat.catalog.margin_cache import MarginCacheCatalogInfo


class MarginCatalog(HealpixDataset):
    """

    """
    # Update CatalogInfoClass, used to check if the catalog_info is the correct type, and
    # set the catalog info to the correct type
    CatalogInfoClass: TypeAlias = MarginCacheCatalogInfo
    catalog_info: CatalogInfoClass

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        catalog_path: str = None,
        storage_options: dict | None = None,
    ) -> None:
        """Initializes a Margin Catalog

        Args:
            catalog_info: CatalogInfo object with catalog metadata
            pixels: Specifies the pixels contained in the catalog. Can be either a
                list of HealpixPixel, `PartitionInfo object`, or a `PixelTree` object
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
            storage_options: dictionary that contains abstract filesystem credentials
        """
        if catalog_info.catalog_type != CatalogType.MARGIN:
            raise ValueError(
                f"Catalog info `catalog_type` must equal {CatalogType.MARGIN}"
            )
        super().__init__(catalog_info, pixels, catalog_path, storage_options)
