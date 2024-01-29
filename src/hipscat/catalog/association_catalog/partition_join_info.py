"""Container class to hold primary-to-join partition metadata"""

from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
import pyarrow as pa
from typing_extensions import Self

from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import FilePointer, file_io, paths
from hipscat.io.parquet_metadata import (
    read_row_group_fragments,
    row_group_stat_single_value,
    write_parquet_metadata_for_batches,
)
from hipscat.pixel_math.healpix_pixel import HealpixPixel


class PartitionJoinInfo:
    """Association catalog metadata with which partitions matches occur in the join"""

    PRIMARY_ORDER_COLUMN_NAME = "Norder"
    PRIMARY_PIXEL_COLUMN_NAME = "Npix"
    JOIN_ORDER_COLUMN_NAME = "join_Norder"
    JOIN_PIXEL_COLUMN_NAME = "join_Npix"

    COLUMN_NAMES = [
        PRIMARY_ORDER_COLUMN_NAME,
        PRIMARY_PIXEL_COLUMN_NAME,
        JOIN_ORDER_COLUMN_NAME,
        JOIN_PIXEL_COLUMN_NAME,
    ]

    def __init__(self, join_info_df: pd.DataFrame) -> None:
        self.data_frame = join_info_df
        self._check_column_names()

    def _check_column_names(self):
        for column in self.COLUMN_NAMES:
            if column not in self.data_frame.columns:
                raise ValueError(f"join_info_df does not contain column {column}")

    def primary_to_join_map(self) -> Dict[HealpixPixel, List[HealpixPixel]]:
        """Generate a map from a single primary pixel to one or more pixels in the join catalog.

        Lots of cute comprehension is happening here, so watch out!
        We create tuple of (primary order/pixel) and [array of tuples of (join order/pixel)]

        Returns:
            dictionary mapping (primary order/pixel) to [array of (join order/pixel)]
        """
        primary_map = self.data_frame.groupby(
            [self.PRIMARY_ORDER_COLUMN_NAME, self.PRIMARY_PIXEL_COLUMN_NAME], group_keys=True
        )
        primary_to_join = [
            (
                HealpixPixel(int(primary_pixel[0]), int(primary_pixel[1])),
                [
                    HealpixPixel(int(object_elem[0]), int(object_elem[1]))
                    for object_elem in join_group.dropna().to_numpy().T[2:4].T
                ],
            )
            for primary_pixel, join_group in primary_map
        ]
        ## Treat the array of tuples as a dictionary.
        primary_to_join = dict(primary_to_join)
        return primary_to_join

    def write_to_metadata_files(self, catalog_path: FilePointer, storage_options: dict = None):
        """Generate parquet metadata, using the known partitions.

        Args:
            catalog_path (FilePointer): base path for the catalog
            storage_options (dict): dictionary that contains abstract filesystem credentials
        """
        batches = [
            [
                pa.RecordBatch.from_arrays(
                    [
                        [primary_pixel.order],
                        [primary_pixel.pixel],
                        [join_pixel.order],
                        [join_pixel.pixel],
                    ],
                    names=self.COLUMN_NAMES,
                )
                for join_pixel in join_pixels
            ]
            for primary_pixel, join_pixels in self.primary_to_join_map().items()
        ]

        write_parquet_metadata_for_batches(batches, catalog_path, storage_options)

    def write_to_csv(self, catalog_path: FilePointer, storage_options: dict = None):
        """Write all partition data to CSV files.

        Two files will be written::
        - partition_info.csv - covers all primary catalog pixels, and should match the file structure
        - partition_join_info.csv - covers all pairwise relationships between primary and
          join catalogs.

        Args:
            catalog_path: FilePointer to the directory where the
                `partition_join_info.csv` file will be written
            storage_options (dict): dictionary that contains abstract filesystem credentials
        """
        partition_join_info_file = paths.get_partition_join_info_pointer(catalog_path)
        file_io.write_dataframe_to_csv(
            self.data_frame, partition_join_info_file, index=False, storage_options=storage_options
        )

        primary_pixels = self.primary_to_join_map().keys()
        partition_info_pointer = paths.get_partition_info_pointer(catalog_path)
        partition_info = PartitionInfo.from_healpix(primary_pixels)
        file_io.write_dataframe_to_csv(
            partition_info.as_dataframe(),
            partition_info_pointer,
            index=False,
            storage_options=storage_options,
        )

    @classmethod
    def read_from_dir(cls, catalog_base_dir: FilePointer, storage_options: dict = None) -> Self:
        """Read partition join info from a file within a hipscat directory.

        This will look for a `_metadata` file, and if not found, will look for
        a `partition_join_info.csv` file.

        Args:
            catalog_base_dir: path to the root directory of the catalog
            storage_options (dict): dictionary that contains abstract filesystem credentials

        Returns:
            A `PartitionInfo` object with the data from the file

        Raises:
            FileNotFoundError: if neither desired file is found in the catalog_base_dir
        """
        metadata_file = paths.get_parquet_metadata_pointer(catalog_base_dir)
        partition_join_info_file = paths.get_partition_join_info_pointer(catalog_base_dir)
        if file_io.does_file_or_directory_exist(metadata_file, storage_options=storage_options):
            partition_join_info = PartitionJoinInfo.read_from_file(
                metadata_file, storage_options=storage_options
            )
        elif file_io.does_file_or_directory_exist(partition_join_info_file, storage_options=storage_options):
            partition_join_info = PartitionJoinInfo.read_from_csv(
                partition_join_info_file, storage_options=storage_options
            )
        else:
            raise FileNotFoundError(
                f"_metadata or partition join info file is required in catalog directory {catalog_base_dir}"
            )
        return partition_join_info

    @classmethod
    def read_from_file(
        cls, metadata_file: FilePointer, strict=False, storage_options: Union[Dict[Any, Any], None] = None
    ) -> Self:
        """Read partition join info from a `_metadata` file to create an object

        Args:
            metadata_file (FilePointer): FilePointer to the `_metadata` file
            storage_options (dict): dictionary that contains abstract filesystem credentials

        Returns:
            A `PartitionJoinInfo` object with the data from the file
        """
        if strict:
            pixel_frame = pd.DataFrame(
                [
                    (
                        row_group_stat_single_value(row_group, cls.PRIMARY_ORDER_COLUMN_NAME),
                        row_group_stat_single_value(row_group, cls.PRIMARY_PIXEL_COLUMN_NAME),
                        row_group_stat_single_value(row_group, cls.JOIN_ORDER_COLUMN_NAME),
                        row_group_stat_single_value(row_group, cls.JOIN_PIXEL_COLUMN_NAME),
                    )
                    for row_group in read_row_group_fragments(metadata_file, storage_options)
                ],
                columns=cls.COLUMN_NAMES,
            )
        else:
            total_metadata = file_io.read_parquet_metadata(metadata_file, storage_options)
            num_row_groups = total_metadata.num_row_groups

            first_row_group = total_metadata.row_group(0)
            norder_column = -1
            npix_column = -1
            join_norder_column = -1
            join_npix_column = -1

            for i in range(0, first_row_group.num_columns):
                column = first_row_group.column(i)
                if column.path_in_schema == cls.PRIMARY_ORDER_COLUMN_NAME:
                    norder_column = i
                elif column.path_in_schema == cls.PRIMARY_PIXEL_COLUMN_NAME:
                    npix_column = i
                elif column.path_in_schema == cls.JOIN_ORDER_COLUMN_NAME:
                    join_norder_column = i
                elif column.path_in_schema == cls.JOIN_PIXEL_COLUMN_NAME:
                    join_npix_column = i

            missing_columns = []
            if norder_column == -1:
                missing_columns.append(cls.PRIMARY_ORDER_COLUMN_NAME)
            if npix_column == -1:
                missing_columns.append(cls.PRIMARY_PIXEL_COLUMN_NAME)
            if join_norder_column == -1:
                missing_columns.append(cls.JOIN_ORDER_COLUMN_NAME)
            if join_npix_column == -1:
                missing_columns.append(cls.JOIN_PIXEL_COLUMN_NAME)

            if len(missing_columns) != 0:
                raise ValueError(f"Metadata missing columns ({missing_columns})")

            row_group_index = np.arange(0, num_row_groups)
            pixel_frame = pd.DataFrame(
                [
                    (
                        total_metadata.row_group(index).column(norder_column).statistics.min,
                        total_metadata.row_group(index).column(npix_column).statistics.min,
                        total_metadata.row_group(index).column(join_norder_column).statistics.min,
                        total_metadata.row_group(index).column(join_npix_column).statistics.min,
                    )
                    for index in row_group_index
                ],
                columns=cls.COLUMN_NAMES,
            )

        return cls(pixel_frame)

    @classmethod
    def read_from_csv(
        cls, partition_join_info_file: FilePointer, storage_options: Union[Dict[Any, Any], None] = None
    ) -> Self:
        """Read partition join info from a `partition_join_info.csv` file to create an object

        Args:
            partition_join_info_file (FilePointer): FilePointer to the `partition_join_info.csv` file
            storage_options (dict): dictionary that contains abstract filesystem credentials

        Returns:
            A `PartitionJoinInfo` object with the data from the file
        """
        if not file_io.does_file_or_directory_exist(
            partition_join_info_file, storage_options=storage_options
        ):
            raise FileNotFoundError(
                f"No partition info found where expected: {str(partition_join_info_file)}"
            )

        data_frame = file_io.load_csv_to_pandas(partition_join_info_file, storage_options=storage_options)
        return cls(data_frame)
