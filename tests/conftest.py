import dataclasses
import os.path
from pathlib import Path
from typing import List

import pandas as pd
import pyarrow as pa
import pytest

from hats.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hats.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hats.catalog.catalog_info import CatalogInfo
from hats.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hats.catalog.margin_cache import MarginCacheCatalogInfo
from hats.inspection.almanac import Almanac
from hats.pixel_math import HealpixPixel

DATA_DIR_NAME = "data"
ALMANAC_DIR_NAME = "almanac"
SMALL_SKY_DIR_NAME = "small_sky"
SMALL_SKY_ORDER1_DIR_NAME = "small_sky_order1"
SMALL_SKY_SOURCE_OBJECT_INDEX_DIR_NAME = "small_sky_source_object_index"

TEST_DIR = os.path.dirname(__file__)

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def test_data_dir():
    return Path(TEST_DIR) / DATA_DIR_NAME


@pytest.fixture
def almanac_dir(test_data_dir):
    return test_data_dir / ALMANAC_DIR_NAME


@pytest.fixture
def small_sky_dir(test_data_dir):
    return test_data_dir / SMALL_SKY_DIR_NAME


@pytest.fixture
def small_sky_order1_dir(test_data_dir):
    return test_data_dir / SMALL_SKY_ORDER1_DIR_NAME


@pytest.fixture
def small_sky_source_object_index_dir(test_data_dir):
    return test_data_dir / SMALL_SKY_SOURCE_OBJECT_INDEX_DIR_NAME


@pytest.fixture
def assert_catalog_info_matches_dict():
    def assert_match(catalog_info: BaseCatalogInfo, dictionary: dict):
        """Check that all members of the catalog_info object match dictionary
        elements, where specified."""
        catalog_info_dict = dataclasses.asdict(catalog_info)
        for key, value in dictionary.items():
            assert catalog_info_dict[key] == value

    return assert_match


@pytest.fixture
def base_catalog_info_data() -> dict:
    return {
        "catalog_name": "test_name",
        "catalog_type": "object",
        "total_rows": 10,
    }


@pytest.fixture
def catalog_info_data() -> dict:
    return {
        "catalog_name": "test_name",
        "catalog_type": "object",
        "total_rows": 10,
        "epoch": "J2000",
        "ra_column": "ra",
        "dec_column": "dec",
    }


@pytest.fixture
def association_catalog_info_data() -> dict:
    return {
        "catalog_name": "test_name",
        "catalog_type": "association",
        "total_rows": 10,
        "primary_catalog": "small_sky",
        "primary_column": "id",
        "primary_column_association": "id_small_sky",
        "join_catalog": "small_sky_order1",
        "join_column": "id",
        "join_column_association": "id_small_sky_order1",
        "contains_leaf_files": False,
    }


@pytest.fixture
def source_catalog_info() -> dict:
    return {
        "catalog_name": "test_source",
        "catalog_type": "source",
        "total_rows": 100,
        "epoch": "J2000",
        "ra_column": "source_ra",
        "dec_column": "source_dec",
    }


@pytest.fixture
def source_catalog_info_with_extra() -> dict:
    return {
        "catalog_name": "test_source",
        "catalog_type": "source",
        "total_rows": 100,
        "epoch": "J2000",
        "ra_column": "source_ra",
        "dec_column": "source_dec",
        "primary_catalog": "test_name",
        "mjd_column": "mjd",
        "band_column": "band",
        "mag_column": "mag",
        "mag_err_column": "",
    }


@pytest.fixture
def margin_cache_catalog_info_data() -> dict:
    return {
        "catalog_name": "test_margin",
        "catalog_type": "margin",
        "total_rows": 100,
        "epoch": "J2000",
        "ra_column": "ra",
        "dec_column": "dec",
        "primary_catalog": "test_name",
        "margin_threshold": 0.5,
    }


@pytest.fixture
def index_catalog_info() -> dict:
    return {
        "catalog_name": "test_index",
        "catalog_type": "index",
        "total_rows": 100,
        "primary_catalog": "test_name",
        "indexing_column": "id",
    }


@pytest.fixture
def index_catalog_info_with_extra() -> dict:
    return {
        "catalog_name": "test_index",
        "catalog_type": "index",
        "total_rows": 100,
        "primary_catalog": "test_name",
        "indexing_column": "id",
        "extra_columns": ["foo", "bar"],
    }


@pytest.fixture
def small_sky_schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
            pa.field("Norder", pa.uint8()),
            pa.field("Dir", pa.uint64()),
            pa.field("Npix", pa.uint64()),
            pa.field("_healpix_29", pa.uint64()),
        ]
    )


@pytest.fixture
def small_sky_source_schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("source_id", pa.int64()),
            pa.field("source_ra", pa.float64()),
            pa.field("source_dec", pa.float64()),
            pa.field("mjd", pa.float64()),
            pa.field("mag", pa.float64()),
            pa.field("band", pa.string()),
            pa.field("object_id", pa.int64()),
            pa.field("object_ra", pa.float64()),
            pa.field("object_dec", pa.float64()),
            pa.field("Norder", pa.uint8()),
            pa.field("Dir", pa.uint64()),
            pa.field("Npix", pa.uint64()),
            pa.field("_healpix_29", pa.uint64()),
        ]
    )


@pytest.fixture
def association_catalog_schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("Norder", pa.int64()),
            pa.field("Npix", pa.int64()),
            pa.field("join_Norder", pa.int64()),
            pa.field("join_Npix", pa.int64()),
        ]
    )


@pytest.fixture
def margin_catalog_schema() -> pa.Schema:
    return pa.schema(
        [
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
            pa.field("Norder", pa.uint8()),
            pa.field("Dir", pa.uint64()),
            pa.field("Npix", pa.uint64()),
            pa.field("_healpix_29", pa.uint64()),
            pa.field("margin_Norder", pa.uint8()),
            pa.field("margin_Dir", pa.uint64()),
            pa.field("margin_Npix", pa.uint64()),
        ]
    )


@pytest.fixture
def dataset_path(test_data_dir) -> str:
    return test_data_dir / "info_only" / "dataset"


@pytest.fixture
def base_catalog_info_file(dataset_path) -> str:
    return dataset_path / "catalog_info.json"


@pytest.fixture
def base_catalog_info(base_catalog_info_data) -> BaseCatalogInfo:
    return BaseCatalogInfo(**base_catalog_info_data)


@pytest.fixture
def catalog_path(test_data_dir) -> str:
    return test_data_dir / "info_only" / "catalog"


@pytest.fixture
def catalog_info_file(catalog_path) -> str:
    return catalog_path / "catalog_info.json"


@pytest.fixture
def catalog_info(catalog_info_data) -> CatalogInfo:
    return CatalogInfo(**catalog_info_data)


@pytest.fixture
def margin_catalog_info(margin_cache_catalog_info_data) -> MarginCacheCatalogInfo:
    return MarginCacheCatalogInfo(**margin_cache_catalog_info_data)


@pytest.fixture
def margin_catalog_pixels() -> List[HealpixPixel]:
    return [
        HealpixPixel(0, 4),
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]


@pytest.fixture
def margin_catalog_path(test_data_dir) -> str:
    return test_data_dir / "small_sky_order1_margin"


@pytest.fixture
def catalog_pixels() -> List[HealpixPixel]:
    return [HealpixPixel(1, 0), HealpixPixel(1, 1), HealpixPixel(2, 8)]


@pytest.fixture
def association_catalog_path(test_data_dir) -> str:
    return test_data_dir / "small_sky_to_small_sky_order1"


@pytest.fixture
def association_catalog_info_file(association_catalog_path) -> str:
    return association_catalog_path / "catalog_info.json"


@pytest.fixture
def index_catalog_info_file(test_data_dir) -> str:
    return test_data_dir / "info_only" / "index_catalog" / "catalog_info.json"


@pytest.fixture
def margin_cache_catalog_info_file(test_data_dir) -> str:
    return test_data_dir / "info_only" / "margin_cache" / "catalog_info.json"


@pytest.fixture
def source_catalog_info_file(test_data_dir) -> str:
    return test_data_dir / "small_sky_source" / "catalog_info.json"


@pytest.fixture
def small_sky_source_dir(test_data_dir) -> str:
    return test_data_dir / "small_sky_source"


@pytest.fixture
def small_sky_source_pixels():
    """Source catalog pixels"""
    return [
        HealpixPixel(0, 4),
        HealpixPixel(2, 176),
        HealpixPixel(2, 177),
        HealpixPixel(2, 178),
        HealpixPixel(2, 179),
        HealpixPixel(2, 180),
        HealpixPixel(2, 181),
        HealpixPixel(2, 182),
        HealpixPixel(2, 183),
        HealpixPixel(2, 184),
        HealpixPixel(2, 185),
        HealpixPixel(2, 186),
        HealpixPixel(2, 187),
        HealpixPixel(1, 47),
    ]


@pytest.fixture
def association_catalog_info(association_catalog_info_data) -> AssociationCatalogInfo:
    return AssociationCatalogInfo(**association_catalog_info_data)


@pytest.fixture
def association_catalog_partition_join_file(association_catalog_path) -> str:
    return association_catalog_path / "partition_join_info.csv"


@pytest.fixture
def association_catalog_join_pixels() -> pd.DataFrame:
    return pd.DataFrame.from_dict(
        {
            PartitionJoinInfo.PRIMARY_ORDER_COLUMN_NAME: [0, 0, 0, 0],
            PartitionJoinInfo.PRIMARY_PIXEL_COLUMN_NAME: [11, 11, 11, 11],
            PartitionJoinInfo.JOIN_ORDER_COLUMN_NAME: [1, 1, 1, 1],
            PartitionJoinInfo.JOIN_PIXEL_COLUMN_NAME: [44, 45, 46, 47],
        }
    )


@pytest.fixture
def default_almanac(almanac_dir, test_data_dir):
    """Set up default environment variables and fetch default almanac data."""
    os.environ["HATS_ALMANAC_DIR"] = str(almanac_dir)
    os.environ["HATS_DEFAULT_DIR"] = str(test_data_dir)

    return Almanac()
