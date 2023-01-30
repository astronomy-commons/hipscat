"""Container class to hold catalog metadata and partition iteration"""

import json
import os

import pandas as pd

import hipscat.io.paths as paths


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
        partition_info_filename = os.path.join(self.catalog_path, "partition_info.csv")
        if not os.path.exists(partition_info_filename):
            raise FileNotFoundError(
                f"No partition info found where expected: {partition_info_filename}"
            )

        with open(metadata_filename, "r", encoding="utf-8") as metadata_info:
            self.metadata_keywords = json.load(metadata_info)
        self.catalog_name = self.metadata_keywords["catalog_name"]
        self.partition_info = pd.read_csv(partition_info_filename).copy()

    def get_pixels(self):
        """Get all healpix pixels that are contained in the catalog

        Returns:
            data frame with per-pixel data.

            The data frame contains the following columns:

            - order: order of the destination pixel
            - pixel: pixel number *at the above order*
            - num_objects: the number of rows in the pixel's partition
        """
        return self.partition_info

    def get_partitions(self):
        """Get file handles for all partition files in the catalog

        Returns:
            one-dimensional array of strings, where each string is a partition file
        """
        file_names = []
        for _, partition in self.partition_info.iterrows():
            file_names.append(
                paths.pixel_catalog_file(
                    self.catalog_path, partition["order"], partition["pixel"]
                )
            )

        return file_names
