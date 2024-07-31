from typing import Any, Dict, Tuple, Union

from typing_extensions import Self

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.io import FilePointer, file_io, paths


class Dataset:
    """A base HiPSCat dataset that contains a catalog_info metadata file
    and the data contained in parquet files"""

    CatalogInfoClass = BaseCatalogInfo

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        catalog_path=None,
        *,
        file_system=None,
        storage_options: Union[Dict[Any, Any], None] = None,
    ) -> None:
        """Initializes a Dataset

        Args:
            catalog_info: A catalog_info object with the catalog metadata
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
            file_system: fsspec or pyarrow filesystem, default None
            storage_options: dictionary that contains abstract filesystem credentials
        """
        if not isinstance(catalog_info, self.CatalogInfoClass):
            raise TypeError(f"catalog_info type must be {self.CatalogInfoClass}")

        self.catalog_info = catalog_info
        self.catalog_name = self.catalog_info.catalog_name

        self.catalog_path = catalog_path
        self.on_disk = catalog_path is not None
        self.file_system = file_system
        self.storage_options = storage_options
        self.catalog_base_dir = file_io.get_file_pointer_from_path(self.catalog_path)

    @classmethod
    def read_from_hipscat(
        cls, catalog_path: str, *, file_system=None, storage_options: Union[Dict[Any, Any], None] = None
    ) -> Self:
        """Reads a HiPSCat Catalog from a HiPSCat directory

        Args:
            catalog_path: path to the root directory of the catalog
            file_system: fsspec or pyarrow filesystem, default None
            storage_options: dictionary that contains abstract filesystem credentials

        Returns:
            The initialized catalog object
        """
        catalog_base_dir = file_io.get_file_pointer_from_path(catalog_path)
        cls._check_files_exist(catalog_base_dir, file_system=file_system, storage_options=storage_options)
        args = cls._read_args(catalog_base_dir, file_system=file_system, storage_options=storage_options)
        kwargs = cls._read_kwargs(catalog_base_dir, file_system=file_system, storage_options=storage_options)
        return cls(*args, **kwargs)

    @classmethod
    def _read_args(
        cls,
        catalog_base_dir: FilePointer,
        *,
        file_system=None,
        storage_options: Union[Dict[Any, Any], None] = None,
    ) -> Tuple[CatalogInfoClass]:
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        catalog_info = cls.CatalogInfoClass.read_from_metadata_file(
            catalog_info_file, file_system=file_system, storage_options=storage_options
        )
        return (catalog_info,)

    @classmethod
    def _read_kwargs(
        cls,
        catalog_base_dir: FilePointer,
        *,
        file_system=None,
        storage_options: Union[Dict[Any, Any], None] = None,
    ) -> dict:
        return {
            "catalog_path": str(catalog_base_dir),
            "file_system": file_system,
            "storage_options": storage_options,
        }

    @classmethod
    def _check_files_exist(
        cls,
        catalog_base_dir: FilePointer,
        *,
        file_system=None,
        storage_options: Union[Dict[Any, Any], None] = None,
    ):
        if not file_io.does_file_or_directory_exist(
            catalog_base_dir, file_system=file_system, storage_options=storage_options
        ):
            raise FileNotFoundError(f"No directory exists at {str(catalog_base_dir)}")
        catalog_info_file = paths.get_catalog_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(
            catalog_info_file, file_system=file_system, storage_options=storage_options
        ):
            raise FileNotFoundError(f"No catalog info found where expected: {str(catalog_info_file)}")
