"""Container class to hold per-partition metadata"""

import os

import pandas as pd

from hipscat.io import paths


class PartitionInfo:
    """Container class for per-partition info."""

    METADATA_ORDER_COLUMN_NAME = "Norder"
    METADATA_DIR_COLUMN_NAME = "Dir"
    METADATA_PIXEL_COLUMN_NAME = "Npix"

    def __init__(self, catalog_path=None):
        self.catalog_path = catalog_path

        partition_info_filename = os.path.join(self.catalog_path, "partition_info.csv")
        if not os.path.exists(partition_info_filename):
            raise FileNotFoundError(
                f"No partition info found where expected: {partition_info_filename}"
            )

        self.data_frame = pd.read_csv(partition_info_filename)

    def get_file_names(self):
        """Get file handles for all partition files in the catalog

        Returns:
            one-dimensional array of strings, where each string is a partition file
        """
        file_names = []
        for _, partition in self.data_frame.iterrows():
            file_names.append(
                paths.pixel_catalog_file(
                    self.catalog_path,
                    partition[self.METADATA_ORDER_COLUMN_NAME],
                    partition[self.METADATA_PIXEL_COLUMN_NAME],
                )
            )

        return file_names
