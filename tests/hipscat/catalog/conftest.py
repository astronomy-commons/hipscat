import dataclasses
import os.path

import pandas as pd
import pytest

from hipscat.catalog import partition_info, PartitionInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo


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
    return pd.DataFrame.from_dict({
        PartitionInfo.METADATA_ORDER_COLUMN_NAME: [1, 1, 2],
        PartitionInfo.METADATA_DIR_COLUMN_NAME: [0, 0, 0],
        PartitionInfo.METADATA_PIXEL_COLUMN_NAME: [0, 1, 8]
    })
