from typing import List, Optional

from jproperties import Properties
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self
from upath import UPath

from hats.catalog.catalog_type import CatalogType
from hats.io import file_io

## catalog_name, catalog_type, and total_rows are allowed for ALL types
CATALOG_TYPE_ALLOWED_FIELDS = {
    CatalogType.OBJECT: ["ra_column", "dec_column"],
    CatalogType.SOURCE: ["primary_catalog", "ra_column", "dec_column"],
    CatalogType.ASSOCIATION: [
        "primary_catalog",
        "primary_column",
        "primary_column_association",
        "join_catalog",
        "join_column",
        "join_column_association",
        "contains_leaf_files",
    ],
    CatalogType.INDEX: ["primary_catalog", "indexing_column", "extra_columns"],
    CatalogType.MARGIN: ["primary_catalog", "margin_threshold", "ra_column", "dec_column"],
}

## catalog_name, catalog_type, and total_rows are required for ALL types
CATALOG_TYPE_REQUIRED_FIELDS = {
    CatalogType.OBJECT: ["ra_column", "dec_column"],
    CatalogType.SOURCE: ["ra_column", "dec_column"],
    CatalogType.ASSOCIATION: [
        "primary_catalog",
        "primary_column",
        "join_catalog",
        "join_column",
        "contains_leaf_files",
    ],
    CatalogType.INDEX: ["primary_catalog", "indexing_column"],
    CatalogType.MARGIN: ["primary_catalog", "margin_threshold"],
}


class TableProperties(BaseModel):
    """Container class for catalog metadata"""

    catalog_name: str = Field(alias="obs_collection")
    catalog_type: CatalogType = Field(alias="dataproduct_type")
    total_rows: int = Field(alias="hats_nrows")

    ra_column: Optional[str] = Field(default=None, alias="hats_col_j2000_ra")
    dec_column: Optional[str] = Field(default=None, alias="hats_col_j2000_dec")

    primary_catalog: Optional[str] = Field(default=None, alias="hats_primary_table_url")
    """Reference to object catalog. Relevant for nested, margin, association, and index"""

    margin_threshold: Optional[float] = Field(default=None, alias="hats_margin_threshold")
    """Threshold of the pixel boundary, expressed in arcseconds."""

    primary_column: Optional[str] = Field(default=None, alias="hats_col_assn_primary")
    """Column name in the primary (left) side of join"""

    primary_column_association: Optional[str] = Field(default=None, alias="hats_col_assn_primary_assn")
    """Column name in the association table that matches the primary (left) side of join"""

    join_catalog: Optional[str] = Field(default=None, alias="hats_assn_join_table_url")
    """Catalog name for the joining (right) side of association"""

    join_column: Optional[str] = Field(default=None, alias="hats_col_assn_join")
    """Column name in the joining (right) side of join"""

    join_column_association: Optional[str] = Field(default=None, alias="hats_col_assn_join_assn")
    """Column name in the association table that matches the joining (right) side of join"""

    contains_leaf_files: Optional[bool] = Field(default=None, alias="hats_assn_leaf_files")
    """Whether or not the association catalog contains leaf parquet files"""

    indexing_column: Optional[str] = Field(default=None, alias="hats_index_column")
    """Column that we provide an index over"""

    extra_columns: Optional[List[str]] = Field(default=None, alias="hats_index_extra_column")
    """Any additional payload columns included in index"""

    ## Allow any extra keyword args to be stored on the properties object.
    model_config = ConfigDict(extra="allow", populate_by_name=True, use_enum_values=True)

    @model_validator(mode="after")
    def check_allowed_and_required(self) -> Self:
        """Check that type-specific fields are appropriate, and required fields are set."""
        explicit_keys = set(
            self.model_dump(by_alias=False, exclude_none=True).keys() - self.__pydantic_extra__.keys()
        )

        allowed_keys = set(
            CATALOG_TYPE_ALLOWED_FIELDS[self.catalog_type] + ["catalog_name", "catalog_type", "total_rows"]
        )
        non_allowed = explicit_keys - allowed_keys
        if len(non_allowed) > 0:
            raise ValueError(f"Unexpected property for table type {self.catalog_type} ({non_allowed})")

        required_keys = set(
            CATALOG_TYPE_REQUIRED_FIELDS[self.catalog_type] + ["catalog_name", "catalog_type", "total_rows"]
        )
        missing_required = required_keys - explicit_keys
        if len(missing_required) > 0:
            raise ValueError(
                f"Missing required property for table type {self.catalog_type} ({missing_required})"
            )
        return self

    def explicit_dict(self):
        """Create a dict, based on fields that have been explicitly set, and are not "extra" keys."""
        explicit = self.model_dump(by_alias=False, exclude_none=True, round_trip=True)
        extra_keys = self.__pydantic_extra__.keys()
        explicit = {(key, val) for key, val in explicit.items() if key not in extra_keys}
        return dict(explicit)

    def __str__(self):
        """Friendly string representation based on named fields."""
        parameters = self.explicit_dict()
        formatted_string = ""
        for name, value in parameters.items():
            formatted_string += f"  {name} {value}\n"
        return formatted_string

    @classmethod
    def read_from_dir(cls, catalog_dir: UPath) -> Self:
        """Read field values from a java-style properties file."""
        file_path = file_io.get_upath(catalog_dir) / "properties"
        if not file_io.does_file_or_directory_exist(file_path):
            raise FileNotFoundError(f"No properties file found where expected: {str(file_path)}")
        p = Properties()
        with file_path.open("rb") as f:
            p.load(f, "utf-8")
        return cls(**p.properties)

    def to_properties_file(self, catalog_dir: UPath) -> Self:
        """Write fields to a java-style properties file."""
        # pylint: disable=protected-access
        parameters = self.model_dump(by_alias=True, exclude_none=True)
        properties = Properties()
        properties.properties = parameters
        properties._key_order = parameters.keys()
        file_path = file_io.get_upath(catalog_dir) / "properties"
        with file_path.open("wb") as _file:
            properties.store(_file, "utf-8", timestamp=False)
