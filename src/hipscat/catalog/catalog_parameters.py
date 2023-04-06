"""Conatiner class for properties of a catalog that is being created"""

from dataclasses import dataclass

from hipscat.io import file_io


@dataclass
class CatalogParameters:
    """Container class for catalog properties"""

    catalog_name: str = ""
    catalog_type: str = "object"
    output_path: str = ""
    epoch: str = "J2000"
    ra_column: str = "ra"
    dec_column: str = "dec"
    total_rows: int = 0

    def __post_init__(
        self,
    ):

        if self.catalog_type not in (
            "object",
            "source",
            "index",
            "association",
            "margin",
        ):
            raise ValueError(f"Unknown catalog type: {self.catalog_type}")

        output_path_pointer = file_io.get_file_pointer_from_path(self.output_path)
        self.catalog_base_dir = file_io.append_paths_to_pointer(
            output_path_pointer, self.catalog_name
        )
        self.catalog_path = str(self.catalog_base_dir)
        file_io.make_directory(self.catalog_base_dir, exist_ok=True)

    def __str__(self):
        formatted_string = (
            f"  catalog_name {self.catalog_name}\n"
            f"  catalog_type {self.catalog_type}\n"
            f"  epoch {self.epoch}\n"
            f"  ra_column {self.ra_column}\n"
            f"  dec_column {self.dec_column}\n"
            f"  total_rows {self.total_rows}\n"
            f"  output_path {self.output_path}\n"
        )
        return formatted_string
