"""Container class to hold catalog metadata and partition iteration"""
from __future__ import annotations
from typing import List, Tuple, Union

import dataclasses

import healpy as hp
import numpy as np

from typing_extensions import TypeAlias
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.healpix_dataset.healpix_dataset import HealpixDataset, PixelInputTypes
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.cone_filter import filter_pixels_by_cone
from hipscat.pixel_tree.pixel_node_type import PixelNodeType


class Catalog(HealpixDataset):
    """A HiPSCat Catalog with data stored in a HEALPix Hive partitioned structure

    Catalogs of this type are partitioned spatially, contain `partition_info` metadata specifying
    the pixels in Catalog, and on disk conform to the parquet partitioning structure
    `Norder=/Dir=/Npix=.parquet`
    """

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
        storage_options: dict = None,
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
        super().__init__(catalog_info, pixels, catalog_path, storage_options)

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
