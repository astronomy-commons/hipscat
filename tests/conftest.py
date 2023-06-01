import dataclasses
import os
import os.path

import pandas as pd
import pytest

from hipscat.catalog import PartitionInfo
from hipscat.catalog.association_catalog.association_catalog_info import \
    AssociationCatalogInfo
from hipscat.catalog.association_catalog.partition_join_info import \
    PartitionJoinInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo

DATA_DIR_NAME = "data"
SMALL_SKY_DIR_NAME = "small_sky"
SMALL_SKY_ORDER1_DIR_NAME = "small_sky_order1"
SMALL_SKY_TO_SMALL_SKY_ORDER1_DIR_NAME = "small_sky_to_small_sky_order1"
TEST_DIR = os.path.dirname(__file__)

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def test_data_dir():
    return os.path.join(TEST_DIR, DATA_DIR_NAME)


@pytest.fixture
def small_sky_dir(test_data_dir):
    return os.path.join(test_data_dir, SMALL_SKY_DIR_NAME)


@pytest.fixture
def small_sky_order1_dir(test_data_dir):
    return os.path.join(test_data_dir, SMALL_SKY_ORDER1_DIR_NAME)


@pytest.fixture
def small_sky_to_small_sky_order1_dir(test_data_dir):
    return os.path.join(test_data_dir, SMALL_SKY_TO_SMALL_SKY_ORDER1_DIR_NAME)


@pytest.fixture
def assert_catalog_info_matches_dict():
    def assert_match(catalog_info: BaseCatalogInfo, dictionary: dict):
        catalog_info_dict = dataclasses.asdict(catalog_info)
        assert catalog_info_dict == dictionary

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
        "join_catalog": "small_sky_order1",
        "join_column": "id",
    }


@pytest.fixture
def dataset_path(test_data_dir) -> str:
    return os.path.join(test_data_dir, "dataset")


@pytest.fixture
def base_catalog_info_file(dataset_path) -> str:
    return os.path.join(dataset_path, "catalog_info.json")


@pytest.fixture
def base_catalog_info(base_catalog_info_data) -> BaseCatalogInfo:
    return BaseCatalogInfo(**base_catalog_info_data)


@pytest.fixture
def catalog_path(test_data_dir) -> str:
    return os.path.join(test_data_dir, "catalog")


@pytest.fixture
def catalog_info_file(catalog_path) -> str:
    return os.path.join(catalog_path, "catalog_info.json")


@pytest.fixture
def catalog_info(catalog_info_data) -> CatalogInfo:
    return CatalogInfo(**catalog_info_data)


@pytest.fixture
def catalog_pixels() -> pd.DataFrame:
    return pd.DataFrame.from_dict(
        {
            PartitionInfo.METADATA_ORDER_COLUMN_NAME: [1, 1, 2],
            PartitionInfo.METADATA_DIR_COLUMN_NAME: [0, 0, 0],
            PartitionInfo.METADATA_PIXEL_COLUMN_NAME: [0, 1, 8],
        }
    )


@pytest.fixture
def association_catalog_path(test_data_dir) -> str:
    return os.path.join(test_data_dir, "small_sky_to_small_sky_order1")


@pytest.fixture
def association_catalog_info_file(association_catalog_path) -> str:
    return os.path.join(association_catalog_path, "catalog_info.json")


@pytest.fixture
def association_catalog_info(association_catalog_info_data) -> AssociationCatalogInfo:
    return AssociationCatalogInfo(**association_catalog_info_data)


@pytest.fixture
def association_catalog_partition_join_file(association_catalog_path) -> str:
    return os.path.join(association_catalog_path, "partition_join_info.csv")


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