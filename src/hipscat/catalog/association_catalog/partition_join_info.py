"""Container class to hold primary-to-join partition metadata"""

import pandas as pd
import pyarrow as pa
from typing_extensions import Self

from hipscat.io import FilePointer, file_io
from hipscat.io.parquet_metadata import (
    read_row_group_fragments,
    row_group_stat_single_value,
    write_parquet_metadata_for_batches,
)


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

    def write_to_metadata_files(self, catalog_path: FilePointer, storage_options: dict = None):
        """Generate parquet metadata, using the known partitions.

        Args:
            catalog_path (str): base path for the catalog
            storage_options: dictionary that contains abstract filesystem credentials
        """
        batches = [
            pa.RecordBatch.from_arrays(
                [
                    [row[self.PRIMARY_ORDER_COLUMN_NAME]],
                    [row[self.PRIMARY_PIXEL_COLUMN_NAME]],
                    [row[self.JOIN_ORDER_COLUMN_NAME]],
                    [row[self.JOIN_PIXEL_COLUMN_NAME]],
                ],
                names=self.COLUMN_NAMES,
            )
            for index, row in self.data_frame.iterrows()
        ]

        write_parquet_metadata_for_batches(batches, catalog_path, storage_options)

    @classmethod
    def read_from_file(cls, metadata_file: FilePointer, storage_options: dict = None):
        """Read partition join info from a `_metadata` file to create an object

        Args:
            metadata_file: FilePointer to the `_metadata` file
            storage_options: dictionary that contains abstract filesystem credentials

        Returns:
            A `PartitionJoinInfo` object with the data from the file
        """
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

        return cls(pixel_frame)

    @classmethod
    def read_from_csv(cls, partition_join_info_file: FilePointer, storage_options: dict = None) -> Self:
        """Read partition join info from a `partition_join_info.csv` file to create an object

        Args:
            partition_join_info_file: FilePointer to the `partition_join_info.csv` file
            storage_options: dictionary that contains abstract filesystem credentials

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
