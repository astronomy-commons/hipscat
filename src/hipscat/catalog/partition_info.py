"""Container class to hold per-partition metadata"""
from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
import pyarrow as pa

from hipscat.io import FilePointer, file_io
from hipscat.io.parquet_metadata import (
    read_row_group_fragments,
    row_group_stat_single_value,
    write_parquet_metadata_for_batches,
)
from hipscat.pixel_math import HealpixPixel


class PartitionInfo:
    """Container class for per-partition info."""

    METADATA_ORDER_COLUMN_NAME = "Norder"
    METADATA_DIR_COLUMN_NAME = "Dir"
    METADATA_PIXEL_COLUMN_NAME = "Npix"

    def __init__(self, pixel_list: List[HealpixPixel]) -> None:
        self.pixel_list = pixel_list

    def get_healpix_pixels(self) -> List[HealpixPixel]:
        """Get healpix pixel objects for all pixels represented as partitions.

        Returns:
            List of HealpixPixel
        """
        return self.pixel_list

    def get_highest_order(self) -> int:
        """Get the highest healpix order for the dataset.

        Returns:
            int representing highest order.
        """
        max_pixel = np.max(self.pixel_list)
        return max_pixel.order

    def write_to_file(self, partition_info_file: FilePointer):
        """Write all partition data to CSV file.

        Args:
            partition_info_file: FilePointer to where the `partition_info.csv`
                file will be written
        """
        file_io.write_dataframe_to_csv(self.as_dataframe(), partition_info_file, index=False)

    def write_to_metadata_files(self, catalog_path: FilePointer, storage_options: dict = None):
        """Generate parquet metadata, using the known partitions.

        Args:
            catalog_path (FilePointer): base path for the catalog
            storage_options (dict): dictionary that contains abstract filesystem credentials
        """
        batches = [
            pa.RecordBatch.from_arrays(
                [[pixel.order], [pixel.dir], [pixel.pixel]],
                names=[
                    self.METADATA_ORDER_COLUMN_NAME,
                    self.METADATA_DIR_COLUMN_NAME,
                    self.METADATA_PIXEL_COLUMN_NAME,
                ],
            )
            for pixel in self.get_healpix_pixels()
        ]

        write_parquet_metadata_for_batches(batches, catalog_path, storage_options)

    @classmethod
    def read_from_file(cls, metadata_file: FilePointer, storage_options: dict = None) -> PartitionInfo:
        """Read partition info from a `_metadata` file to create an object

        Args:
            metadata_file (FilePointer): FilePointer to the `_metadata` file
            storage_options (dict): dictionary that contains abstract filesystem credentials

        Returns:
            A `PartitionInfo` object with the data from the file
        """
        pixel_list = [
            HealpixPixel(
                row_group_stat_single_value(row_group, cls.METADATA_ORDER_COLUMN_NAME),
                row_group_stat_single_value(row_group, cls.METADATA_PIXEL_COLUMN_NAME),
            )
            for row_group in read_row_group_fragments(metadata_file, storage_options)
        ]
        ## Remove duplicates, preserving order.
        ## In the case of association partition join info, we may have multiple entries
        ## for the primary order/pixels.
        pixel_list = list(dict.fromkeys(pixel_list))

        return cls(pixel_list)

    @classmethod
    def read_from_csv(cls, partition_info_file: FilePointer, storage_options: dict = None) -> PartitionInfo:
        """Read partition info from a `partition_info.csv` file to create an object

        Args:
            partition_info_file (FilePointer): FilePointer to the `partition_info.csv` file
            storage_options (dict): dictionary that contains abstract filesystem credentials

        Returns:
            A `PartitionInfo` object with the data from the file
        """
        if not file_io.does_file_or_directory_exist(partition_info_file, storage_options=storage_options):
            raise FileNotFoundError(f"No partition info found where expected: {str(partition_info_file)}")

        data_frame = file_io.load_csv_to_pandas(partition_info_file, storage_options=storage_options)

        pixel_list = [
            HealpixPixel(order, pixel)
            for order, pixel in zip(
                data_frame[cls.METADATA_ORDER_COLUMN_NAME],
                data_frame[cls.METADATA_PIXEL_COLUMN_NAME],
            )
        ]

        return cls(pixel_list)

    def as_dataframe(self):
        """Construct a pandas dataframe for the partition info pixels.

        Returns:
            Dataframe with order, directory, and pixel info.
        """
        partition_info_dict = {
            PartitionInfo.METADATA_ORDER_COLUMN_NAME: [],
            PartitionInfo.METADATA_PIXEL_COLUMN_NAME: [],
            PartitionInfo.METADATA_DIR_COLUMN_NAME: [],
        }
        for pixel in self.pixel_list:
            partition_info_dict[PartitionInfo.METADATA_ORDER_COLUMN_NAME].append(pixel.order)
            partition_info_dict[PartitionInfo.METADATA_PIXEL_COLUMN_NAME].append(pixel.pixel)
            partition_info_dict[PartitionInfo.METADATA_DIR_COLUMN_NAME].append(
                int(pixel.pixel / 10_000) * 10_000
            )
        return pd.DataFrame.from_dict(partition_info_dict)

    @classmethod
    def from_healpix(cls, healpix_pixels: List[HealpixPixel]) -> PartitionInfo:
        """Create a partition info object from a list of constituent healpix pixels.

        Args:
            healpix_pixels: list of healpix pixels
        Returns:
            A `PartitionInfo` object with the same healpix pixels
        """
        return cls(healpix_pixels)
