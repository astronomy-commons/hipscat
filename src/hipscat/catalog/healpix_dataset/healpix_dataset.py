from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Tuple, Union

import healpy as hp
import numpy as np
import pandas as pd
from mocpy import MOC
from typing_extensions import Self, TypeAlias

from hipscat.catalog.dataset import BaseCatalogInfo, Dataset
from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import FilePointer, file_io, paths
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree import PixelAlignmentType, PixelAlignment
from hipscat.pixel_tree.moc_filter import filter_by_moc
from hipscat.pixel_tree.pixel_alignment import align_with_mocs
from hipscat.pixel_tree.pixel_tree import PixelTree

PixelInputTypes = Union[PartitionInfo, PixelTree, List[HealpixPixel]]


class HealpixDataset(Dataset):
    """A HiPSCat dataset partitioned with a HEALPix partitioning structure.

    Catalogs of this type are partitioned based on the ra and dec of the points with each partition
    containing points within a given HEALPix pixel. The files are in the form::

        Norder=/Dir=/Npix=.parquet
    """

    CatalogInfoClass: TypeAlias = BaseCatalogInfo
    catalog_info: CatalogInfoClass

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        catalog_path: str = None,
        moc: MOC | None = None,
        storage_options: Union[Dict[Any, Any], None] = None,
    ) -> None:
        """Initializes a Catalog

        Args:
            catalog_info: CatalogInfo object with catalog metadata
            pixels: Specifies the pixels contained in the catalog. Can be either a
                list of HealpixPixel, `PartitionInfo object`, or a `PixelTree` object
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
            storage_options: dictionary that contains abstract filesystem credentials
            moc (mocpy.MOC): MOC object representing the coverage of the catalog
        """
        super().__init__(catalog_info, catalog_path=catalog_path, storage_options=storage_options)
        self.partition_info = self._get_partition_info_from_pixels(pixels)
        self.pixel_tree = self._get_pixel_tree_from_pixels(pixels)
        self.moc = moc

    def get_healpix_pixels(self) -> List[HealpixPixel]:
        """Get healpix pixel objects for all pixels contained in the catalog.

        Returns:
            List of HealpixPixel
        """
        return self.partition_info.get_healpix_pixels()

    @staticmethod
    def _get_partition_info_from_pixels(pixels: PixelInputTypes) -> PartitionInfo:
        if isinstance(pixels, PartitionInfo):
            return pixels
        if isinstance(pixels, PixelTree):
            return PartitionInfo.from_healpix(pixels.get_healpix_pixels())
        if pd.api.types.is_list_like(pixels):
            return PartitionInfo.from_healpix(pixels)
        raise TypeError("Pixels must be of type PartitionInfo, PixelTree, or List[HealpixPixel]")

    @staticmethod
    def _get_pixel_tree_from_pixels(pixels: PixelInputTypes) -> PixelTree:
        if isinstance(pixels, PartitionInfo):
            return PixelTree.from_healpix(pixels.get_healpix_pixels())
        if isinstance(pixels, PixelTree):
            return pixels
        if pd.api.types.is_list_like(pixels):
            return PixelTree.from_healpix(pixels)
        raise TypeError("Pixels must be of type PartitionInfo, PixelTree, or List[HealpixPixel]")

    @classmethod
    def _read_args(
        cls,
        catalog_base_dir: FilePointer,
        storage_options: Union[Dict[Any, Any], None] = None,
    ) -> Tuple[CatalogInfoClass, PartitionInfo]:
        args = super()._read_args(catalog_base_dir, storage_options=storage_options)
        partition_info = PartitionInfo.read_from_dir(catalog_base_dir, storage_options=storage_options)
        return args + (partition_info,)

    @classmethod
    def _read_kwargs(
        cls, catalog_base_dir: FilePointer, storage_options: Union[Dict[Any, Any], None] = None
    ) -> dict:
        kwargs = super()._read_kwargs(catalog_base_dir, storage_options=storage_options)
        kwargs["moc"] = cls._read_moc_from_point_map(catalog_base_dir, storage_options)
        return kwargs

    @classmethod
    def _read_moc_from_point_map(
        cls, catalog_base_dir: FilePointer, storage_options: Union[Dict[Any, Any], None] = None
    ) -> MOC | None:
        """Reads a MOC object from the `point_map.fits` file if it exists in the catalog directory"""
        point_map_path = paths.get_point_map_file_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(point_map_path, storage_options=storage_options):
            return None
        fits_image = file_io.read_fits_image(point_map_path, storage_options=storage_options)
        order = hp.nside2order(hp.npix2nside(len(fits_image)))
        boolean_skymap = fits_image.astype(bool)
        ipix = np.where(boolean_skymap)[0]
        orders = np.full(ipix.shape, order)
        return MOC.from_healpix_cells(ipix, orders, order)

    @classmethod
    def _check_files_exist(cls, catalog_base_dir: FilePointer, storage_options: dict = None):
        super()._check_files_exist(catalog_base_dir, storage_options=storage_options)

        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        metadata_file = paths.get_parquet_metadata_pointer(catalog_base_dir)
        if not (
            file_io.does_file_or_directory_exist(partition_info_file, storage_options=storage_options)
            or file_io.does_file_or_directory_exist(metadata_file, storage_options=storage_options)
        ):
            raise FileNotFoundError(
                f"_metadata or partition info file is required in catalog directory {catalog_base_dir}"
            )

    def filter_from_pixel_list(self, pixels: List[HealpixPixel]) -> Self:
        """Filter the pixels in the catalog to only include the requested pixels.

        Args:
            pixels (List[HealpixPixels]): the pixels to include

        Returns:
            A new catalog with only those pixels. Note that we reset the total_rows
            to None, instead of performing a scan over the new pixel sizes.
        """
        filtered_catalog_info = dataclasses.replace(self.catalog_info, total_rows=None)
        return self.__class__(filtered_catalog_info, pixels)

    def align(
        self, other_cat: Self, alignment_type: PixelAlignmentType = PixelAlignmentType.INNER
    ) -> PixelAlignment:
        left_moc = self.moc if self.moc is not None else self.pixel_tree.to_moc()
        right_moc = other_cat.moc if other_cat is not None else other_cat.pixel_tree.to_moc()
        return align_with_mocs(
            self.pixel_tree, other_cat.pixel_tree, left_moc, right_moc, alignment_type=alignment_type
        )
