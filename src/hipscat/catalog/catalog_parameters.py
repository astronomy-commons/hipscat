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

    CATALOG_TYPES = [
        "object",
        "source",
        "index",
        "association",
        "margin",
    ]

    def __post_init__(
        self,
    ):

        if self.catalog_type not in self.CATALOG_TYPES:
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


def read_from_metadata_file(catalog_info_file):
    """Read catalog parameters from a catalog_info.json file. Validate the parameters"""
    metadata_keywords = file_io.load_json_file(catalog_info_file)
    catalog_name = metadata_keywords["catalog_name"]
    if not catalog_name:
        raise ValueError("Catalog name is required in catalog info file.")

    catalog_type = metadata_keywords.get("catalog_type", "object")
    if catalog_type not in CatalogParameters.CATALOG_TYPES:
        raise ValueError(f"Unknown catalog type: {catalog_type}")

    return CatalogParameters(
        catalog_name=catalog_name,
        catalog_type=catalog_type,
        epoch=metadata_keywords.get("epoch", "J2000"),
        ra_column=metadata_keywords.get("ra_column", "ra"),
        dec_column=metadata_keywords.get("dec_column", "dec"),
        total_rows=int(metadata_keywords.get("total_rows", 0)),
    )
