import dataclasses
import os
import os.path

import pytest

from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo

DATA_DIR_NAME = "data"
ALMANAC_DIR_NAME = "almanac"
SMALL_SKY_DIR_NAME = "small_sky"
SMALL_SKY_ORDER1_DIR_NAME = "small_sky_order1"
SMALL_SKY_TO_SMALL_SKY_ORDER1_DIR_NAME = "small_sky_to_small_sky_order1"

# pylint: disable=missing-function-docstring, redefined-outer-name


def pytest_addoption(parser):
    parser.addoption("--cloud", action="store", default="abfs")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.cloud
    if "cloud" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("cloud", [option_value])


@pytest.fixture
def example_cloud_path(cloud):
    if cloud == "abfs":
        return "abfs://hipscat/pytests/hipscat"

    raise NotImplementedError("Cloud format not implemented for hipscat tests!")


@pytest.fixture
def example_cloud_storage_options(cloud):
    if cloud == "abfs":
        storage_options = {
            "account_key": os.environ.get("ABFS_LINCCDATA_ACCOUNT_KEY"),
            "account_name": os.environ.get("ABFS_LINCCDATA_ACCOUNT_NAME"),
        }
        return storage_options

    return {}


@pytest.fixture
def tmp_dir_cloud(example_cloud_path):
    return os.path.join(example_cloud_path, "tmp")


@pytest.fixture
def test_data_dir_cloud(example_cloud_path):
    return os.path.join(example_cloud_path, DATA_DIR_NAME)


@pytest.fixture
def almanac_dir_cloud(test_data_dir_cloud):
    return os.path.join(test_data_dir_cloud, ALMANAC_DIR_NAME)


@pytest.fixture
def small_sky_dir_cloud(test_data_dir_cloud):
    return os.path.join(test_data_dir_cloud, SMALL_SKY_DIR_NAME)


@pytest.fixture
def small_sky_order1_dir_cloud(test_data_dir_cloud):
    return os.path.join(test_data_dir_cloud, SMALL_SKY_ORDER1_DIR_NAME)


@pytest.fixture
def base_catalog_info_file_cloud(test_data_dir_cloud) -> str:
    return os.path.join(test_data_dir_cloud, "dataset", "catalog_info.json")


@pytest.fixture
def catalog_info_file_cloud(catalog_path_cloud) -> str:
    return os.path.join(catalog_path_cloud, "catalog_info.json")


@pytest.fixture
def small_sky_dir_local():
    cloud_test_path = os.path.dirname(__file__)
    return os.path.join(cloud_test_path, "..", "tests", "data", SMALL_SKY_DIR_NAME)


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
def catalog_info(catalog_info_data) -> CatalogInfo:
    return CatalogInfo(**catalog_info_data)
