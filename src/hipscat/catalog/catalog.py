"""Container class to hold catalog metadata and partition iteration"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pyarrow as pa
from mocpy import MOC
from typing_extensions import TypeAlias
from upath import UPath

import hipscat.pixel_math.healpix_shim as hp
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.healpix_dataset.healpix_dataset import HealpixDataset, PixelInputTypes
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.box_filter import generate_box_moc, wrap_ra_angles
from hipscat.pixel_math.cone_filter import generate_cone_moc
from hipscat.pixel_math.polygon_filter import CartesianCoordinates, SphericalCoordinates, generate_polygon_moc
from hipscat.pixel_math.validators import (
    validate_box_search,
    validate_declination_values,
    validate_polygon,
    validate_radius,
)
from hipscat.pixel_tree.negative_tree import compute_negative_tree_pixels


class Catalog(HealpixDataset):
    """A HiPSCat Catalog with data stored in a HEALPix Hive partitioned structure

    Catalogs of this type are partitioned spatially, contain `partition_info` metadata specifying
    the pixels in Catalog, and on disk conform to the parquet partitioning structure
    `Norder=/Dir=/Npix=.parquet`
    """

    HIPS_CATALOG_TYPES = [CatalogType.OBJECT, CatalogType.SOURCE]

    # Update CatalogInfoClass, used to check if the catalog_info is the correct type, and
    # set the catalog info to the correct type
    CatalogInfoClass: TypeAlias = CatalogInfo
    catalog_info: CatalogInfoClass

    def __init__(
        self,
        catalog_info: CatalogInfoClass,
        pixels: PixelInputTypes,
        catalog_path: str | Path | UPath | None = None,
        moc: MOC | None = None,
        schema: pa.Schema | None = None,
    ) -> None:
        """Initializes a Catalog

        Args:
            catalog_info: CatalogInfo object with catalog metadata
            pixels: Specifies the pixels contained in the catalog. Can be either a
                list of HealpixPixel, `PartitionInfo object`, or a `PixelTree` object
            catalog_path: If the catalog is stored on disk, specify the location of the catalog
                Does not load the catalog from this path, only store as metadata
            moc (mocpy.MOC): MOC object representing the coverage of the catalog
            schema (pa.Schema): The pyarrow schema for the catalog
        """
        if catalog_info.catalog_type not in self.HIPS_CATALOG_TYPES:
            raise ValueError(
                f"Catalog info `catalog_type` must be one of "
                f"{', '.join([t.value for t in self.HIPS_CATALOG_TYPES])}"
            )
        super().__init__(
            catalog_info,
            pixels,
            catalog_path=catalog_path,
            moc=moc,
            schema=schema,
        )

    def filter_by_cone(self, ra: float, dec: float, radius_arcsec: float) -> Catalog:
        """Filter the pixels in the catalog to only include the pixels that overlap with a cone

        Args:
            ra (float): Right Ascension of the center of the cone in degrees
            dec (float): Declination of the center of the cone in degrees
            radius_arcsec (float): Radius of the cone in arcseconds

        Returns:
            A new catalog with only the pixels that overlap with the specified cone
        """
        validate_radius(radius_arcsec)
        validate_declination_values(dec)
        return self.filter_by_moc(generate_cone_moc(ra, dec, radius_arcsec, self.get_max_coverage_order()))

    def filter_by_box(
        self, ra: Tuple[float, float] | None = None, dec: Tuple[float, float] | None = None
    ) -> Catalog:
        """Filter the pixels in the catalog to only include the pixels that overlap with a
        right ascension or declination range. In case both ranges are provided, filtering
        is performed using a polygon.

        Args:
            ra (Tuple[float, float]): Right ascension range, in degrees
            dec (Tuple[float, float]): Declination range, in degrees

        Returns:
            A new catalog with only the pixels that overlap with the specified region
        """
        ra = tuple(wrap_ra_angles(ra)) if ra else None
        validate_box_search(ra, dec)
        return self.filter_by_moc(generate_box_moc(ra, dec, self.get_max_coverage_order()))

    def filter_by_polygon(self, vertices: List[SphericalCoordinates] | List[CartesianCoordinates]) -> Catalog:
        """Filter the pixels in the catalog to only include the pixels that overlap
        with a polygonal sky region.

        Args:
            vertices (List[SphericalCoordinates] | List[CartesianCoordinates]): The vertices
                of the polygon to filter points with, in lists of (ra,dec) or (x,y,z) points
                on the unit sphere.

        Returns:
            A new catalog with only the pixels that overlap with the specified polygon.
        """
        if all(len(vertex) == 2 for vertex in vertices):
            ra, dec = np.array(vertices).T
            validate_declination_values(dec)
            # Get the coordinates vector on the unit sphere if we were provided
            # with polygon spherical coordinates of ra and dec
            cart_vertices = hp.ang2vec(ra, dec, lonlat=True)
        else:
            cart_vertices = vertices
        validate_polygon(cart_vertices)
        return self.filter_by_moc(generate_polygon_moc(cart_vertices, self.get_max_coverage_order()))

    def generate_negative_tree_pixels(self) -> List[HealpixPixel]:
        """Get the leaf nodes at each healpix order that have zero catalog data.

        For example, if an example catalog only had data points in pixel 0 at
        order 0, then this method would return order 0's pixels 1 through 11.
        Used for getting full coverage on margin caches.

        Returns:
            List of HealpixPixels representing the 'negative tree' for the catalog.
        """
        return compute_negative_tree_pixels(self.pixel_tree)
