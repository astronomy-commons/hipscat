import pytest
import os

from hipscat.catalog import Catalog
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType

# pylint: disable= redefined-outer-name


@pytest.fixture
def root_pixel_node_data():
    return {
        "pixel": HealpixPixel(-1, -1),
        "node_type": PixelNodeType.ROOT,
        "parent": None,
    }


@pytest.fixture
def root_pixel_node(root_pixel_node_data):
    return PixelNode(**root_pixel_node_data)


@pytest.fixture
def inner_pixel_node_data(root_pixel_node):
    return {
        "pixel": HealpixPixel(0, 1),
        "node_type": PixelNodeType.INNER,
        "parent": root_pixel_node,
    }


@pytest.fixture
def inner_pixel_node(inner_pixel_node_data):
    return PixelNode(**inner_pixel_node_data)


@pytest.fixture
def leaf_pixel_node_data(inner_pixel_node):
    return {
        "pixel": HealpixPixel(1, 12),
        "node_type": PixelNodeType.LEAF,
        "parent": inner_pixel_node,
    }


@pytest.fixture
def leaf_pixel_node(leaf_pixel_node_data):
    return PixelNode(**leaf_pixel_node_data)


@pytest.fixture
def small_sky_catalog(small_sky_dir):
    return Catalog.read_from_hipscat(small_sky_dir)


@pytest.fixture()
def small_sky_pixels():
    return [
        HealpixPixel(0, 11),
    ]


@pytest.fixture
def small_sky_order1_catalog(small_sky_order1_dir):
    return Catalog.read_from_hipscat(small_sky_order1_dir)


@pytest.fixture
def small_sky_order1_catalog_abfs(example_abfs_path, example_abfs_storage_options):
    small_sky_order1_dir = os.path.join(
        example_abfs_path, "data", "small_sky_order1"
    )
    return Catalog.read_from_hipscat(small_sky_order1_dir, storage_options=example_abfs_storage_options)

@pytest.fixture()
def small_sky_order1_pixels():
    return [
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]


@pytest.fixture
def example_abfs_path():
    return "abfs:///hipscat/pytests"


@pytest.fixture
def example_abfs_storage_options():
    storage_options = {
        "account_key" : os.environ.get("ABFS_LINCCDATA_ACCOUNT_KEY"),
        "account_name" : os.environ.get("ABFS_LINCCDATA_ACCOUNT_NAME")
    }
    return storage_options


@pytest.fixture
def example_s3_file_path():
    return "s3://hipscat/pytests"


@pytest.fixture
def example_s3_storage_options():
    storage_options = {
        "key" : os.environ.get("AWS_S3_HIPSCAT_ACCOUNT_KEY"),
        "secret" : os.environ.get("AWS_S3_HIPSCAT_ACCOUNT_SECRET")
    }
    return storage_options