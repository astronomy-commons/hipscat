"""Conatiner class for properties of a catalog that is being created"""

import os


class CatalogParameters:
    """Container class for catalog properties"""

    def __init__(
        self,
        catalog_name=None,
        input_paths=None,
        input_format="csv",
        output_path=None,
        highest_healpix_order=10,
        pixel_threshold=1_000_000,
        ra_column="ra",
        dec_column="dec",
        id_column="id",
    ):
        self.catalog_name = catalog_name
        self.input_format = input_format
        self.input_paths = input_paths
        self.output_path = output_path
        self.catalog_path = os.path.join(output_path, catalog_name)
        os.makedirs(self.catalog_path, exist_ok=True)

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
            f"  ra_column {self.ra_column}\n"
            f"  dec_column {self.dec_column}\n"
            f"  id_column {self.id_column}\n"
            f"  output_path {self.output_path}\n"
            f"  highest_healpix_order {self.highest_healpix_order}\n"
            f"  pixel_threshold {self.pixel_threshold}\n"
        )
        return formatted_string
