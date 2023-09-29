"""Container class to hold catalog metadata and partition iteration"""
from __future__ import annotations
from typing import List, Tuple, Union

import dataclasses

import healpy as hp
import numpy as np
import pandas as pd

from typing_extensions import TypeAlias
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.dataset.dataset import Dataset
from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import FilePointer, file_io, paths
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.cone_filter import filter_pixels_by_cone
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


class Catalog(Dataset):
    """A HiPSCat Catalog with data stored in a HEALPix Hive partitioned structure

    Catalogs of this type are partitioned spatially, contain `partition_info` metadata specifying
    the pixels in Catalog, and on disk conform to the parquet partitioning structure
    `Norder=/Dir=/Npix=.parquet`
    """

    PixelInputTypes = Union[pd.DataFrame, PartitionInfo, PixelTree, List[HealpixPixel]]
    HIPS_CATALOG_TYPES = [CatalogType.OBJECT, CatalogType.SOURCE, CatalogType.MARGIN]

    # Update CatalogInfoClass, used to check if the catalog_info is the correct type, and
    # set the catalog info to the correct type
    CatalogInfoClass: TypeAlias = CatalogInfo
    catalog_info: CatalogInfoClass

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        catalog_path: str = None,
        storage_options: dict = None
    ) -> None:
        """Initializes a Catalog

        Args:
            catalog_info: CatalogInfo object with catalog metadata
            pixels: Specifies the pixels contained in the catalog. Can be either a Dataframe with
                columns `Norder`, `Dir`, and `Npix` matching a `partition_info.csv` file, a
                `PartitionInfo object`, or a `PixelTree` object
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
            storage_options: dictionary that contains abstract filesystem credentials
        """
        if catalog_info.catalog_type not in self.HIPS_CATALOG_TYPES:
            raise ValueError(
                f"Catalog info `catalog_type` must be one of "
                f"{', '.join([t.value for t in self.HIPS_CATALOG_TYPES])}"
            )
        super().__init__(catalog_info, catalog_path, storage_options)
        self.partition_info = self._get_partition_info_from_pixels(pixels)
        self.pixel_tree = self._get_pixel_tree_from_pixels(pixels)

    @staticmethod
    def _get_partition_info_from_pixels(pixels: PixelInputTypes) -> PartitionInfo:
        if isinstance(pixels, PartitionInfo):
            return pixels
        if isinstance(pixels, pd.DataFrame):
            return PartitionInfo(pixels)
        if isinstance(pixels, PixelTree):
            return PartitionInfo.from_healpix(
                [
                    HealpixPixel(node.hp_order, node.hp_pixel)
                    for node in pixels.root_pixel.get_all_leaf_descendants()
                ]
            )
        if pd.api.types.is_list_like(pixels):
            return PartitionInfo.from_healpix(pixels)
        raise TypeError("Pixels must be of type PartitionInfo, Dataframe, PixelTree, or List[HealpixPixel]")

    @staticmethod
    def _get_pixel_tree_from_pixels(pixels: PixelInputTypes) -> PixelTree:
        if isinstance(pixels, PartitionInfo):
            return PixelTreeBuilder.from_partition_info_df(pixels.data_frame)
        if isinstance(pixels, pd.DataFrame):
            return PixelTreeBuilder.from_partition_info_df(pixels)
        if isinstance(pixels, PixelTree):
            return pixels
        if pd.api.types.is_list_like(pixels):
            return PixelTreeBuilder.from_healpix(pixels)
        raise TypeError("Pixels must be of type PartitionInfo, Dataframe, PixelTree, or List[HealpixPixel]")

    def get_pixels(self):
        """Get all healpix pixels that are contained in the catalog

        Returns:
            data frame with per-pixel data.

            The data frame contains the following columns:

            - order: order of the destination pixel
            - pixel: pixel number *at the above order*
            - num_objects: the number of rows in the pixel's partition
        """
        return self.partition_info.data_frame

    def get_healpix_pixels(self) -> List[HealpixPixel]:
        """Get healpix pixel objects for all pixels contained in the catalog.

        Returns:
            List of HealpixPixel
        """
        return self.partition_info.get_healpix_pixels()

    @classmethod
    def _read_args(
        cls, catalog_base_dir: FilePointer, storage_options: dict = None
    ) -> Tuple[CatalogInfoClass, PartitionInfo]:
        args = super()._read_args(catalog_base_dir, storage_options=storage_options)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        partition_info = PartitionInfo.read_from_file(partition_info_file, storage_options=storage_options)
        return args + (partition_info,)

    @classmethod
    def _check_files_exist(cls, catalog_base_dir: FilePointer, storage_options: dict = None):
        super()._check_files_exist(catalog_base_dir, storage_options=storage_options)
        partition_info_file = paths.get_partition_info_pointer(catalog_base_dir)
        if not file_io.does_file_or_directory_exist(partition_info_file, storage_options=storage_options):
            raise FileNotFoundError(f"No partition info found where expected: {str(partition_info_file)}")

    def filter_by_cone(self, ra: float, dec: float, radius: float) -> Catalog:
        """Filter the pixels in the catalog to only include the pixels that overlap with a cone

        Args:
            ra (float): Right Ascension of the center of the cone in degrees
            dec (float): Declination of the center of the cone in degrees
            radius (float): Radius of the cone in degrees

        Returns:
            A new catalog with only the pixels that overlap with the specified cone
        """
        filtered_cone_pixels = filter_pixels_by_cone(self.pixel_tree, ra, dec, radius)
        filtered_catalog_info = dataclasses.replace(
            self.catalog_info,
            total_rows=None,
        )
        return Catalog(filtered_catalog_info, filtered_cone_pixels)

    # pylint: disable=too-many-locals
    def generate_negative_tree_pixels(self) -> List[HealpixPixel]:
        """Get the leaf nodes at each healpix order that have zero catalog data.

        For example, if an example catalog only had data points in pixel 0 at
        order 0, then this method would return order 0's pixels 1 through 11.
        Used for getting full coverage on margin caches.

        Returns:
            List of HealpixPixels representing the 'negative tree' for the catalog.
        """
        max_depth = self.partition_info.get_highest_order()
        missing_pixels = []
        pixels_at_order = self.pixel_tree.root_pixel.children

        covered_orders = []
        for order_i in range(0, max_depth + 1):
            npix = hp.nside2npix(2**order_i)
            covered_orders.append(np.zeros(npix))

        for order in range(0, max_depth + 1):
            next_order_children = []
            leaf_pixels = []

            for node in pixels_at_order:
                pixel = node.pixel.pixel
                covered_orders[order][pixel] = 1
                if node.node_type == PixelNodeType.LEAF:
                    leaf_pixels.append(pixel)
                else:
                    next_order_children.extend(node.children)

            zero_leafs = np.argwhere(covered_orders[order] == 0).flatten()
            for pix in zero_leafs:
                missing_pixels.append(HealpixPixel(order, pix))
                leaf_pixels.append(pix)

            pixels_at_order = next_order_children

            for order_j in range(order + 1, max_depth + 1):
                explosion_factor = 4 ** (order_j - order)
                for pixel in leaf_pixels:
                    covered_pix = range(pixel * explosion_factor, (pixel + 1) * explosion_factor)
                    covered_orders[order_j][covered_pix] = 1

        return missing_pixels
