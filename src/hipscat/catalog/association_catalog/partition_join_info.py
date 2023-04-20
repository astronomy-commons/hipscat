import pandas as pd
from typing_extensions import Self

from hipscat.io import FilePointer, file_io


class PartitionJoinInfo:
    """Association catalog metadata with which partitions matches occur in the join"""

    PRIMARY_ORDER_COLUMN_NAME = "primary_Norder"
    PRIMARY_PIXEL_COLUMN_NAME = "primary_Npix"
    JOIN_ORDER_COLUMN_NAME = "join_Norder"
    JOIN_PIXEL_PIXEL_NAME = "join_Npix"

    def __init__(self, join_info_df: pd.DataFrame) -> None:
        self.data_frame = join_info_df

    @classmethod
    def read_from_file(cls, partition_join_info_file: FilePointer) -> Self:
        """Read partition join info from a `partition_join_info.csv` file to create an object

        Args:
            partition_join_info_file: FilePointer to the `partition_join_info.csv` file

        Returns:
            A `PartitionJoinInfo` object with the data from the file
        """
        if not file_io.does_file_or_directory_exist(partition_join_info_file):
            raise FileNotFoundError(
                f"No partition info found where expected: {str(partition_join_info_file)}"
            )

        data_frame = file_io.load_csv_to_pandas(partition_join_info_file)
        return cls(data_frame)
