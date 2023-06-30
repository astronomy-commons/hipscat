import dataclasses
import os
from dataclasses import dataclass, field
from typing import List

import yaml
from typing_extensions import Self

from hipscat.catalog.dataset import catalog_info_factory
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.io import file_io


@dataclass
class AlmanacInfo:
    """Container for parsed almanac information."""

    file_path: str = ""
    namespace: str = ""
    catalog_path: str = ""
    catalog_name: str = ""
    catalog_type: str = ""
    primary: str = None
    join: str = None
    primary_link: Self = None
    join_link: Self = None
    sources: List[Self] = field(default_factory=list)
    objects: List[Self] = field(default_factory=list)
    margins: List[Self] = field(default_factory=list)
    associations: List[Self] = field(default_factory=list)
    associations_right: List[Self] = field(default_factory=list)
    indexes: List[Self] = field(default_factory=list)

    creators: List[str] = field(default_factory=list)
    description: str = ""
    version: str = ""
    deprecated: str = ""

    catalog_info: dict = field(default_factory=dict)

    catalog_info_object: BaseCatalogInfo = None

    def __post_init__(self):
        if len(self.catalog_info):
            self.catalog_info_object = catalog_info_factory.create_catalog_info(self.catalog_info)
            if self.catalog_info and "primary_catalog" in self.catalog_info and not self.primary:
                self.primary = self.catalog_info["primary_catalog"]
            if self.catalog_info and "join_catalog" in self.catalog_info and not self.join:
                self.join = self.catalog_info["join_catalog"]

        ## Allows use of $HIPSCAT_DEFAULT_DIR in paths
        self.catalog_path = os.path.expandvars(self.catalog_path)

    @staticmethod
    def get_default_dir() -> str:
        """Fetch the default directory for environment variables.

        This is set via the environment variable: HIPSCAT_ALMANAC_DIR

        To set this in a linux-like environment, use a command like:

            export HIPSCAT_ALMANAC_DIR=/data/path/to/almanacs

        This will also attempt to expand any environment variables WITHIN the default
        directory environment variable. This can be useful in cases where:

            $HIPSCAT_ALMANAC_DIR=$HIPSCAT_DEFAULT_DIR/almanacs/
        """
        default_dir = os.getenv("HIPSCAT_ALMANAC_DIR", "")
        if default_dir:
            default_dir = os.path.expandvars(default_dir)
        return default_dir

    @classmethod
    def from_catalog_dir(cls, catalog_base_dir: str) -> Self:
        """Create almanac information from the catalog information found at the target directory"""
        catalog_info = catalog_info_factory.from_catalog_dir(catalog_base_dir=catalog_base_dir)
        args = {
            "catalog_path": catalog_base_dir,
            "catalog_name": catalog_info.catalog_name,
            "catalog_type": catalog_info.catalog_type,
            "catalog_info_object": catalog_info,
            "catalog_info": dataclasses.asdict(catalog_info),
        }
        return cls(**args)

    @classmethod
    def from_file(cls, file: str) -> Self:
        """Create almanac information from an almanac file."""
        _, fmt = os.path.splitext(file)
        with open(file, "r", encoding="utf-8") as file_handle:
            if fmt == ".yml":
                metadata = yaml.safe_load(file_handle)
            else:
                raise ValueError(f"Unsupported file format {fmt}")
        return cls(**metadata)

    def write_to_file(self, directory=None, default_dir=True, fmt="yml"):
        """Write the almanac to an almanac file"""
        if default_dir and directory:
            raise ValueError("Use only one of dir and default_dir")

        if default_dir:
            directory = AlmanacInfo.get_default_dir()

        file_path = file_io.append_paths_to_pointer(
            file_io.get_file_pointer_from_path(directory), f"{self.catalog_name}.{fmt}"
        )
        if file_io.does_file_or_directory_exist(file_path):
            raise ValueError(f"File already exists at path {str(file_path)}")

        args = {
            "catalog_path": self.catalog_path,
            "catalog_name": self.catalog_name,
            "catalog_type": self.catalog_type,
            "creators": self.creators,
            "description": self.description,
            "catalog_info": self.catalog_info,
        }
        if self.primary:
            args["primary"] = self.primary
        if self.join:
            args["join"] = self.join
        if self.version:
            args["version"] = self.version
        if self.deprecated:
            args["deprecated"] = self.deprecated

        if fmt == "yml":
            encoded_string = yaml.dump(args, sort_keys=False)
        else:
            raise ValueError(f"Unsupported file format {fmt}")

        file_io.write_string_to_file(file_path, encoded_string)
