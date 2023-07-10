"""Container class to hold per-partition metadata"""

from typing import List

import numpy as np
import pandas as pd

from hipscat.io import FilePointer, file_io
from hipscat.pixel_math import HealpixPixel


class PartitionInfo:
    """Container class for per-partition info."""

    METADATA_ORDER_COLUMN_NAME = "Norder"
    METADATA_DIR_COLUMN_NAME = "Dir"
    METADATA_PIXEL_COLUMN_NAME = "Npix"

    def __init__(self, pixels: pd.DataFrame) -> None:
        self.data_frame = pixels

    def get_healpix_pixels(self) -> List[HealpixPixel]:
        """Get healpix pixel objects for all pixels represented as partitions.

        Returns:
            List of HealpixPixel
        """
        return [
            HealpixPixel(order, pixel)
            for order, pixel in zip(
                self.data_frame[self.METADATA_ORDER_COLUMN_NAME],
                self.data_frame[self.METADATA_PIXEL_COLUMN_NAME],
            )
        ]

    def get_highest_order(self) -> int:
        """Get the highest healpix order for the dataset.

        Returns:
            int representing highest order.
        """
        highest_order = np.max(self.data_frame[self.METADATA_ORDER_COLUMN_NAME].values)

        return highest_order

    @classmethod
    def read_from_file(cls, partition_info_file: FilePointer):
        """Read partition info from a `partition_info.csv` file to create an object

        Args:
            partition_info_file: FilePointer to the `partition_info.csv` file

        Returns:
            A `PartitionInfo` object with the data from the file
        """
        if not file_io.does_file_or_directory_exist(partition_info_file):
            raise FileNotFoundError(f"No partition info found where expected: {str(partition_info_file)}")

        data_frame = file_io.load_csv_to_pandas(partition_info_file)
        return cls(data_frame)
