from typing import Type

from typing_extensions import Self

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.io import FilePointer, file_io, paths


class Dataset:
    CatalogInfoClass: Type[BaseCatalogInfo] = BaseCatalogInfo

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        on_disk=False,
        catalog_path=None,
    ) -> None:
        if not isinstance(catalog_info, self.CatalogInfoClass):
            raise TypeError(f"catalog_info type must be {self.CatalogInfoClass}")

        self.catalog_info = catalog_info
        self.catalog_name = self.catalog_info.catalog_name

        if on_disk and catalog_path is None:
            raise ValueError("Catalog Path must be specified for on disk catalog")
        self.on_disk = on_disk
        self.catalog_path = catalog_path
        self.catalog_base_dir = file_io.get_file_pointer_from_path(self.catalog_path)

    @classmethod
    def read_from_hipscat(cls, catalog_path: str) -> Self:
        catalog_base_dir = file_io.get_file_pointer_from_path(catalog_path)
        cls.check_files_exist(catalog_base_dir)
        args = cls.read_args(catalog_base_dir)
        kwargs = cls.read_kwargs(catalog_base_dir)
        return cls(*args, **kwargs)

    @classmethod
    def read_args(cls, catalog_base_dir: FilePointer) -> tuple[CatalogInfoClass]:
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        catalog_info = cls.CatalogInfoClass.read_from_metadata_file(catalog_info_file)
        return catalog_info,

    @classmethod
    def read_kwargs(cls, catalog_base_dir: FilePointer) -> dict:
        return {"on_disk": True, "catalog_path": str(catalog_base_dir)}

    @classmethod
    def check_files_exist(cls, catalog_base_dir: FilePointer):
        if not file_io.does_file_or_directory_exist(catalog_base_dir):
            raise FileNotFoundError(f"No directory exists at {str(catalog_base_dir)}")
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(catalog_info_file):
            raise FileNotFoundError(
                f"No catalog info found where expected: {str(catalog_info_file)}"
            )
