from typing import Tuple, Union

import pandas as pd

from hipscat.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.dataset import Dataset
from hipscat.io import FilePointer, paths


class AssociationCatalog(Dataset):
    """A HiPSCat Catalog for enabling fast joins between two HiPSCat catalogs

    Catalogs of this type are partitioned based on the partitioning of both joining catalogs in the
    form 'Norder=/Dir=/Npix=/join_Norder=/join_Dir=/join_Npix=.parquet'. Where each partition
    contains the matching pair of hipscat indexes from each catalog's respective partitions to join.
    The `partition_join_info` metadata file specifies all pairs of pixels in the Association
    Catalog, corresponding to each pair of partitions in each catalog that contain rows to join.
    """

    CatalogInfoClass = AssociationCatalogInfo
    JoinPixelInputTypes = Union[list, pd.DataFrame, PartitionJoinInfo]

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        join_pixels: JoinPixelInputTypes,
        catalog_path=None,
    ) -> None:
        if not catalog_info.catalog_type == CatalogType.ASSOCIATION:
            raise ValueError("Catalog info `catalog_type` must be 'association'")
        super().__init__(catalog_info, catalog_path)
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
    def _read_args(cls, catalog_base_dir: FilePointer) -> Tuple[CatalogInfoClass, JoinPixelInputTypes]:
        args = super()._read_args(catalog_base_dir)
        partition_join_info_file = paths.get_partition_join_info_pointer(catalog_base_dir)
        partition_join_info = PartitionJoinInfo.read_from_file(partition_join_info_file)
        return args + (partition_join_info,)
