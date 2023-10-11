from typing import Tuple, Union
import pandas as pd
from typing_extensions import TypeAlias

from hipscat.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.healpix_dataset.healpix_dataset import HealpixDataset, PixelInputTypes
from hipscat.io import FilePointer, paths, file_io


class AssociationCatalog(HealpixDataset):
    """A HiPSCat Catalog for enabling fast joins between two HiPSCat catalogs

    Catalogs of this type are partitioned based on the partitioning of the left catalog.
    The `partition_join_info` metadata file specifies all pairs of pixels in the Association
    Catalog, corresponding to each pair of partitions in each catalog that contain rows to join.
    """

    # Update CatalogInfoClass, used to check if the catalog_info is the correct type, and
    # set the catalog info to the correct type
    CatalogInfoClass: TypeAlias = AssociationCatalogInfo
    catalog_info: CatalogInfoClass

    JoinPixelInputTypes = Union[list, pd.DataFrame, PartitionJoinInfo]

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        join_pixels: JoinPixelInputTypes,
        catalog_path=None,
        storage_options: dict = None,
    ) -> None:
        if not catalog_info.catalog_type == CatalogType.ASSOCIATION:
            raise ValueError("Catalog info `catalog_type` must be 'association'")
        super().__init__(catalog_info, pixels, catalog_path, storage_options=storage_options)
        self.join_info = self._get_partition_join_info_from_pixels(join_pixels)

    def get_join_pixels(self) -> pd.DataFrame:
        """Get join pixels listing all pairs of pixels from left and right catalogs that contain
        matching association rows

        Returns:
            pd.DataFrame with each row being a pair of pixels from the primary and join catalogs
        """
        return self.join_info.data_frame

    @staticmethod
    def _get_partition_join_info_from_pixels(
        join_pixels: JoinPixelInputTypes,
    ) -> PartitionJoinInfo:
        if isinstance(join_pixels, PartitionJoinInfo):
            return join_pixels
        if isinstance(join_pixels, pd.DataFrame):
            return PartitionJoinInfo(join_pixels)
        raise TypeError("join_pixels must be of type PartitionJoinInfo or DataFrame")

    @classmethod
    def _read_args(
        cls, catalog_base_dir: FilePointer, storage_options: dict = None
    ) -> Tuple[CatalogInfoClass, PixelInputTypes, JoinPixelInputTypes]:  # type: ignore[override]
        args = super()._read_args(catalog_base_dir, storage_options=storage_options)
        partition_join_info_file = paths.get_partition_join_info_pointer(catalog_base_dir)
        partition_join_info = PartitionJoinInfo.read_from_file(
            partition_join_info_file, storage_options=storage_options
        )
        return args + (partition_join_info,)

    @classmethod
    def _check_files_exist(cls, catalog_base_dir: FilePointer, storage_options: dict = None):
        super()._check_files_exist(catalog_base_dir, storage_options=storage_options)
        partition_join_info_file = paths.get_partition_join_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(
            partition_join_info_file, storage_options=storage_options
        ):
            raise FileNotFoundError(
                f"No partition join info found where expected: {str(partition_join_info_file)}"
            )
