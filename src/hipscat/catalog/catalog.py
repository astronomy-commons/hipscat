"""Container class to hold catalog metadata and partition iteration"""


from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import file_io, paths


class Catalog:
    """Container class for catalog metadata"""

    def __init__(self, catalog_path: str = None) -> None:
        self.catalog_path = catalog_path
        self.catalog_base_dir = file_io.get_file_pointer_from_path(catalog_path)
        self.metadata_keywords = None

        self.partition_info = None

        self.catalog_name = None

        self._initialize_metadata()

    def _initialize_metadata(self):
        if not file_io.does_file_or_directory_exist(self.catalog_base_dir):
            raise FileNotFoundError(
                f"No directory exists at {str(self.catalog_base_dir)}"
            )
        catalog_info_file = paths.get_catalog_info_pointer(self.catalog_base_dir)
        if not file_io.does_file_or_directory_exist(catalog_info_file):
            raise FileNotFoundError(
                f"No catalog info found where expected: {str(catalog_info_file)}"
            )

        self.metadata_keywords = file_io.load_json_file(catalog_info_file)
        self.catalog_name = self.metadata_keywords["catalog_name"]

        self.catalog_type = self.metadata_keywords.get("catalog_type", "object")
        if self.catalog_type not in (
            "object",
            "source",
            "index",
            "association",
            "margin",
        ):
            raise ValueError(f"Unknown catalog type: {self.catalog_type}")

        if self.catalog_type in ("object", "source"):
            self.partition_info = PartitionInfo(self.catalog_base_dir)

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
