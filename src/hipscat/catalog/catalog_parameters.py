"""Conatiner class for properties of a catalog that is being created"""

from typing import List

from hipscat.io import file_io


# pylint: disable=too-many-instance-attributes
class CatalogParameters:
    """Container class for catalog properties"""

    def __init__(
        self,
        catalog_name=None,
        input_paths: List[str] = None,
        input_format="csv",
        output_path=None,
        highest_healpix_order=10,
        pixel_threshold=1_000_000,
        epoch="J2000",
        ra_column="ra",
        dec_column="dec",
        id_column="id",
    ):
        self.catalog_name = catalog_name
        self.input_format = input_format
        self.input_paths = input_paths
        self.output_path = output_path
        output_path_pointer = file_io.get_file_pointer_from_path(self.output_path)
        self.catalog_base_dir = file_io.append_paths_to_pointer(
            output_path_pointer, self.catalog_name
        )
        self.catalog_path = str(self.catalog_base_dir)
        file_io.make_directory(self.catalog_base_dir, exist_ok=True)

        self.epoch = epoch
        self.ra_column = ra_column
        self.dec_column = dec_column
        self.id_column = id_column

        self.highest_healpix_order = highest_healpix_order
        self.pixel_threshold = pixel_threshold

    def __str__(self):
        formatted_string = (
            f"  catalog_name {self.catalog_name}\n"
            f"  input format {self.input_format}\n"
            f"  num input_paths {len(self.input_paths)}\n"
            f"  epoch {self.epoch}\n"
            f"  ra_column {self.ra_column}\n"
            f"  dec_column {self.dec_column}\n"
            f"  id_column {self.id_column}\n"
            f"  output_path {self.output_path}\n"
            f"  highest_healpix_order {self.highest_healpix_order}\n"
            f"  pixel_threshold {self.pixel_threshold}\n"
        )
        return formatted_string
