"""Container class to hold catalog metadata and partition iteration"""
from __future__ import annotations

from typing import Union

import pandas as pd

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.dataset import Dataset
from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import FilePointer, file_io, paths
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


class Catalog(Dataset):
    """Container class for catalog metadata"""

    CatalogInfoClass = CatalogInfo
    PixelInputTypes = Union[dict, list, pd.DataFrame, PixelTree, PartitionInfo]
    HIPS_CATALOG_TYPES = [CatalogType.OBJECT, CatalogType.SOURCE, CatalogType.MARGIN]

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        on_disk=False,
        catalog_path=None,
    ) -> None:
        if catalog_info.catalog_type not in self.HIPS_CATALOG_TYPES:
            raise ValueError(
                f"Catalog info `catalog_type` must be one of "
                f"{', '.join([t.value for t in self.HIPS_CATALOG_TYPES])}"
            )
        super().__init__(catalog_info, on_disk, catalog_path)
        self.partition_info = self._get_partition_info_from_pixels(pixels)
        self.pixel_tree = self._get_pixel_tree_from_pixels(pixels)

    @staticmethod
    def _get_partition_info_from_pixels(pixels: PixelInputTypes) -> PartitionInfo:
        if isinstance(pixels, PartitionInfo):
            return pixels
        if isinstance(pixels, pd.DataFrame):
            return PartitionInfo(pixels)

    @staticmethod
    def _get_pixel_tree_from_pixels(pixels: PixelInputTypes) -> PixelTree:
        if isinstance(pixels, PartitionInfo):
            return PixelTreeBuilder.from_partition_info_df(pixels.data_frame)
        if isinstance(pixels, pd.DataFrame):
            return PixelTreeBuilder.from_partition_info_df(pixels)

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
    def _read_args(cls, catalog_base_dir: FilePointer) -> tuple[CatalogInfoClass, PartitionInfo]:
        args = super()._read_args(catalog_base_dir)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        partition_info = PartitionInfo.read_from_file(partition_info_file)
        return args + (partition_info,)

    @classmethod
    def check_files_exist(cls, catalog_base_dir: FilePointer):
        super().check_files_exist(catalog_base_dir)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(partition_info_file):
            raise FileNotFoundError(
                f"No partition info found where expected: {str(partition_info_file)}"
            )
