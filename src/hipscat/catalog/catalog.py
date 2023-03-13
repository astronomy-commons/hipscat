"""Container class to hold catalog metadata and partition iteration"""

import json
import os

from hipscat.catalog.partition_info import PartitionInfo


class Catalog:
    """Container class for catalog metadata"""

    def __init__(self, catalog_path=None):
        self.catalog_path = catalog_path
        self.metadata_keywords = None

        self.partition_info = None

        self.catalog_name = None

        self._initialize_metadata()

    def _initialize_metadata(self):
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(f"No directory exists at {self.catalog_path}")
        metadata_filename = os.path.join(self.catalog_path, "catalog_info.json")
        if not os.path.exists(metadata_filename):
            raise FileNotFoundError(
                f"No catalog info found where expected: {metadata_filename}"
            )

        with open(metadata_filename, "r", encoding="utf-8") as metadata_info:
            self.metadata_keywords = json.load(metadata_info)
        self.catalog_name = self.metadata_keywords["catalog_name"]
        self.partition_info = PartitionInfo(self.catalog_path)

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
