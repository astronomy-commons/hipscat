import dataclasses
import os
from dataclasses import dataclass, field
from typing import List

from typing_extensions import Self

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.catalog.dataset.catalog_info_factory import (create_catalog_info,
                                                          from_catalog_dir)


@dataclass
class AlmanacCatalogInfo:
    """Container for parsed almanac information."""

    file_path: str = ""
    namespace: str = ""
    catalog_path: str = ""
    catalog_name: str = ""
    catalog_type: str = ""
    primary: str = ""
    join: str = ""
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

    def __post_init__(
        self,
    ):
        if len(self.catalog_info):
            self.catalog_info_object = create_catalog_info(self.catalog_info)

        ## Allows use of $HIPSCAT_DEFAULT_DIR in paths
        self.catalog_path = os.path.expandvars(self.catalog_path)

    @classmethod
    def from_catalog_dir(cls, catalog_base_dir: str) -> Self:
        """Create almanac information from the catalog information found at the target directory"""
        catalog_info = from_catalog_dir(catalog_base_dir=catalog_base_dir)
        args = {
            "catalog_path":catalog_base_dir,
            "catalog_name": catalog_info.catalog_name,
            "catalog_type": catalog_info.catalog_type,
            "catalog_info_object":catalog_info,
            "catalog_info": dataclasses.asdict(catalog_info),
        }
        return cls(args)
