from __future__ import annotations

from pathlib import Path
from typing import Tuple

from typing_extensions import Self
from upath import UPath

from hats.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hats.io import file_io, paths


class Dataset:
    """A base HATS dataset that contains a catalog_info metadata file
    and the data contained in parquet files"""

    CatalogInfoClass = BaseCatalogInfo

    def __init__(
        self, catalog_info: CatalogInfoClass, catalog_path: str | Path | UPath | None = None
    ) -> None:
        """Initializes a Dataset

        Args:
            catalog_info: A catalog_info object with the catalog metadata
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
        """
        if not isinstance(catalog_info, self.CatalogInfoClass):
            raise TypeError(f"catalog_info type must be {self.CatalogInfoClass}")

        self.catalog_info = catalog_info
        self.catalog_name = self.catalog_info.catalog_name

        self.catalog_path = catalog_path
        self.on_disk = catalog_path is not None
        self.catalog_base_dir = file_io.get_upath(self.catalog_path)

    @classmethod
    def read_hats(cls, catalog_path: str | Path | UPath) -> Self:
        """Reads a HATS Catalog from a HATS directory

        Args:
            catalog_path: path to the root directory of the catalog

        Returns:
            The initialized catalog object
        """
        catalog_base_dir = file_io.get_upath(catalog_path)
        cls._check_files_exist(catalog_base_dir)
        args = cls._read_args(catalog_base_dir)
        kwargs = cls._read_kwargs(catalog_base_dir)
        return cls(*args, **kwargs)

    @classmethod
    def _read_args(cls, catalog_base_dir: str | Path | UPath) -> Tuple[CatalogInfoClass]:
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        catalog_info = cls.CatalogInfoClass.read_from_metadata_file(catalog_info_file)
        return (catalog_info,)

    @classmethod
    def _read_kwargs(cls, catalog_base_dir: str | Path | UPath) -> dict:
        return {"catalog_path": catalog_base_dir}

    @classmethod
    def _check_files_exist(cls, catalog_base_dir: str | Path | UPath):
        if not file_io.does_file_or_directory_exist(catalog_base_dir):
            raise FileNotFoundError(f"No directory exists at {str(catalog_base_dir)}")
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(catalog_info_file):
            raise FileNotFoundError(f"No catalog info found where expected: {str(catalog_info_file)}")
