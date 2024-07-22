from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, Union

from typing_extensions import Self

from hipscat.catalog.catalog_type import CatalogType
from hipscat.io import FilePointer, file_io


@dataclass
class BaseCatalogInfo:
    """Container class for catalog metadata"""

    catalog_name: str = ""
    catalog_type: CatalogType | None = None
    total_rows: int | None = None

    DEFAULT_TYPE = None
    """The default catalog type for this catalog info type. To be overridden by subclasses.
    If specified, we will use this value when no catalog_type is provided."""

    REQUIRED_TYPE = None
    """The required catalog type for this catalog info type. To be overridden by subclasses.
    If specified, the catalog MUST have this type."""

    required_fields = ["catalog_type"]

    def __post_init__(self):
        if not self.catalog_type and self.DEFAULT_TYPE:
            self.catalog_type = self.DEFAULT_TYPE
        elif self.REQUIRED_TYPE and self.catalog_type != self.REQUIRED_TYPE:
            raise ValueError(f"Catalog must have type {self.REQUIRED_TYPE}")
        self._check_required_fields()
        if self.catalog_type not in CatalogType.all_types():
            raise ValueError(f"Unknown catalog type: {self.catalog_type}")

    def __str__(self):
        parameters = dataclasses.asdict(self)
        formatted_string = ""
        for name, value in parameters.items():
            formatted_string += f"  {name} {value}\n"
        return formatted_string

    @classmethod
    def read_from_metadata_file(
        cls,
        catalog_info_file: FilePointer,
        *,
        file_system=None,
        storage_options: Union[Dict[Any, Any], None] = None,
    ) -> Self:
        """Read catalog info from the `catalog_info.json` metadata file

        Args:
            catalog_info_file: FilePointer pointing to the `catalog_info.json` file
            file_system: fsspec or pyarrow filesystem, default None
            storage_options: dictionary that contains abstract filesystem credentials

        Returns:
            A CatalogInfo object with the data from the `catalog_info.json` file
        """
        print("catalog_info_file", catalog_info_file)
        metadata_keywords = file_io.load_json_file(
            catalog_info_file, file_system=file_system, storage_options=storage_options
        )
        catalog_info_keywords = {}
        for field in dataclasses.fields(cls):
            if field.name in metadata_keywords:
                catalog_info_keywords[field.name] = metadata_keywords[field.name]
        return cls(**catalog_info_keywords)

    def _check_required_fields(self):
        fields_dict = dataclasses.asdict(self)
        for field_name in self.required_fields:
            if field_name not in fields_dict or fields_dict[field_name] is None:
                raise ValueError(f"{field_name} is required in the Catalog Info and a value must be provided")
