import dataclasses
from dataclasses import dataclass
from typing import Any

from typing_extensions import Self

from hipscat.catalog.catalog_type import CatalogType
from hipscat.io import FilePointer, file_io


@dataclass
class BaseCatalogInfo:
    """Container class for catalog properties"""

    catalog_name: str = ""
    catalog_type: CatalogType = None
    total_rows: int = None

    CATALOG_TYPES = [t.value for t in CatalogType]

    required_fields = ["catalog_type"]

    def __post_init__(
        self,
    ):
        self.check_required_fields()
        if self.catalog_type not in self.CATALOG_TYPES:
            raise ValueError(f"Unknown catalog type: {self.catalog_type}")

    def __str__(self):
        parameters = dataclasses.asdict(self)
        formatted_string = ""
        for name, value in parameters.items():
            formatted_string += f"  {name} {value}\n"
        return formatted_string

    @classmethod
    def read_from_metadata_file(cls, catalog_info_file: FilePointer) -> Self:
        metadata_keywords = file_io.load_json_file(catalog_info_file)
        catalog_info_keywords = {}
        for field in dataclasses.fields(cls):
            if field.name in metadata_keywords:
                catalog_info_keywords[field.name] = metadata_keywords[field.name]
        return cls(**catalog_info_keywords)

    def check_required_fields(self):
        fields_dict = dataclasses.asdict(self)
        for field_name in self.required_fields:
            if field_name not in fields_dict or fields_dict[field_name] is None:
                raise ValueError(
                    f"{field_name} is required in the Catalog Info and a value must be provided"
                )
