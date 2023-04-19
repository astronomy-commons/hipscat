import dataclasses
from dataclasses import dataclass

from typing_extensions import Self

from hipscat.catalog.catalog_type import CatalogType
from hipscat.io import FilePointer, file_io


@dataclass
class BaseCatalogInfo:
    """Container class for catalog properties"""

    catalog_name: str = ""
    catalog_type: CatalogType = None
    catalog_path: str = None
    total_rows: int = None

    CATALOG_TYPES = [t.value for t in CatalogType]

    def __post_init__(
        self,
    ):
        if self.catalog_type not in self.CATALOG_TYPES:
            raise ValueError(f"Unknown catalog type: {self.catalog_type}")
        self.catalog_base_dir = None
        if self.catalog_path is not None:
            self.catalog_base_dir = file_io.get_file_pointer_from_path(
                self.catalog_path
            )

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
