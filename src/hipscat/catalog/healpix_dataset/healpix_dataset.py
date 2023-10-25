from typing import Any, Dict, List, Tuple, Union

import pandas as pd
from typing_extensions import TypeAlias

from hipscat.catalog.dataset import BaseCatalogInfo, Dataset
from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import FilePointer, file_io, paths
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder

PixelInputTypes = Union[PartitionInfo, PixelTree, List[HealpixPixel]]


class HealpixDataset(Dataset):
    """A HiPSCat dataset partitioned with a HEALPix partitioning structure.

    Catalogs of this type are partitioned based on the ra and dec of the points with each partition
    containing points within a given HEALPix pixel. The files are in the form 'Norder=/Dir=/Npix=.parquet'.
    """

    CatalogInfoClass: TypeAlias = BaseCatalogInfo
    catalog_info: CatalogInfoClass

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        catalog_path: str = None,
        storage_options: Dict[Any, Any] | None = None,
    ) -> None:
        """Initializes a Catalog

        Args:
            catalog_info: CatalogInfo object with catalog metadata
            pixels: Specifies the pixels contained in the catalog. Can be either a
                list of HealpixPixel, `PartitionInfo object`, or a `PixelTree` object
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
            storage_options: dictionary that contains abstract filesystem credentials
        """
        super().__init__(catalog_info, catalog_path, storage_options)
        self.partition_info = self._get_partition_info_from_pixels(pixels)
        self.pixel_tree = self._get_pixel_tree_from_pixels(pixels)

    def get_healpix_pixels(self) -> List[HealpixPixel]:
        """Get healpix pixel objects for all pixels contained in the catalog.

        Returns:
            List of HealpixPixel
        """
        return self.partition_info.get_healpix_pixels()

    @staticmethod
    def _get_partition_info_from_pixels(pixels: PixelInputTypes) -> PartitionInfo:
        if isinstance(pixels, PartitionInfo):
            return pixels
        if isinstance(pixels, PixelTree):
            return PartitionInfo.from_healpix(
                [
                    HealpixPixel(node.hp_order, node.hp_pixel)
                    for node in pixels.root_pixel.get_all_leaf_descendants()
                ]
            )
        if pd.api.types.is_list_like(pixels):
            return PartitionInfo.from_healpix(pixels)
        raise TypeError("Pixels must be of type PartitionInfo, PixelTree, or List[HealpixPixel]")

    @staticmethod
    def _get_pixel_tree_from_pixels(pixels: PixelInputTypes) -> PixelTree:
        if isinstance(pixels, PartitionInfo):
            return PixelTreeBuilder.from_healpix(pixels.get_healpix_pixels())
        if isinstance(pixels, PixelTree):
            return pixels
        if pd.api.types.is_list_like(pixels):
            return PixelTreeBuilder.from_healpix(pixels)
        raise TypeError("Pixels must be of type PartitionInfo, PixelTree, or List[HealpixPixel]")

    @classmethod
    def _read_args(
        cls, catalog_base_dir: FilePointer, storage_options: Dict[Any, Any] | None = None
    ) -> Tuple[CatalogInfoClass, PartitionInfo]:
        args = super()._read_args(catalog_base_dir, storage_options=storage_options)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        partition_info = PartitionInfo.read_from_file(partition_info_file, storage_options=storage_options)
        return args + (partition_info,)

    @classmethod
    def _check_files_exist(cls, catalog_base_dir: FilePointer, storage_options: Dict[Any, Any] | None = None):
        super()._check_files_exist(catalog_base_dir, storage_options=storage_options)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(partition_info_file, storage_options=storage_options):
            raise FileNotFoundError(f"No partition info found where expected: {str(partition_info_file)}")
