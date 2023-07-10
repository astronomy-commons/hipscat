"""Container class to hold catalog metadata and partition iteration"""
from __future__ import annotations

from typing import Tuple, Union

import pandas as pd

from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.dataset import Dataset
from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import FilePointer, file_io, paths
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


class Catalog(Dataset):
    """A HiPSCat Catalog with data stored in a HEALPix Hive partitioned structure

    Catalogs of this type are partitioned spatially, contain `partition_info` metadata specifying
    the pixels in Catalog, and on disk conform to the parquet partitioning structure
    `Norder=/Dir=/Npix=.parquet`
    """

    CatalogInfoClass = CatalogInfo
    PixelInputTypes = Union[pd.DataFrame, PartitionInfo]
    HIPS_CATALOG_TYPES = [CatalogType.OBJECT, CatalogType.SOURCE, CatalogType.MARGIN]

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        catalog_path: str = None,
    ) -> None:
        """Initializes a Catalog

        Args:
            catalog_info: CatalogInfo object with catalog metadata
            pixels: Specifies the pixels contained in the catalog. Can be either a Dataframe with
                columns `Norder`, `Dir`, and `Npix` matching a `partition_info.csv` file, or a
                PartitionInfo object
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
        """
        if catalog_info.catalog_type not in self.HIPS_CATALOG_TYPES:
            raise ValueError(
                f"Catalog info `catalog_type` must be one of "
                f"{', '.join([t.value for t in self.HIPS_CATALOG_TYPES])}"
            )
        super().__init__(catalog_info, catalog_path)
        self.partition_info = self._get_partition_info_from_pixels(pixels)
        self.pixel_tree = self._get_pixel_tree_from_pixels(pixels)

    @staticmethod
    def _get_partition_info_from_pixels(pixels: PixelInputTypes) -> PartitionInfo:
        if isinstance(pixels, PartitionInfo):
            return pixels
        if isinstance(pixels, pd.DataFrame):
            return PartitionInfo(pixels)
        raise TypeError("Pixels must be of type PartitionInfo or Dataframe")

    @staticmethod
    def _get_pixel_tree_from_pixels(pixels: PixelInputTypes) -> PixelTree:
        if isinstance(pixels, PartitionInfo):
            return PixelTreeBuilder.from_partition_info_df(pixels.data_frame)
        if isinstance(pixels, pd.DataFrame):
            return PixelTreeBuilder.from_partition_info_df(pixels)
        raise TypeError("Pixels must be of type PartitionInfo or Dataframe")

    def get_pixels(self):
        """Get all healpix pixels that are contained in the catalog

        Returns:
            data frame with per-pixel data.

            The data frame contains the following columns:

            - order: order of the destination pixel
            - pixel: pixel number *at the above order*
            - num_objects: the number of rows in the pixel's partition
        """
        return self.partition_info.data_frame

    @classmethod
    def _read_args(cls, catalog_base_dir: FilePointer) -> Tuple[CatalogInfoClass, PartitionInfo]:
        args = super()._read_args(catalog_base_dir)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        partition_info = PartitionInfo.read_from_file(partition_info_file)
        return args + (partition_info,)

    @classmethod
    def _check_files_exist(cls, catalog_base_dir: FilePointer):
        super()._check_files_exist(catalog_base_dir)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(partition_info_file):
            raise FileNotFoundError(f"No partition info found where expected: {str(partition_info_file)}")
