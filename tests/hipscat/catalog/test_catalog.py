"""Tests of catalog functionality"""

import os

from hipscat.catalog import Catalog

TEST_DIR = os.path.dirname(__file__)

TEST_DATA_DIR = os.path.join(TEST_DIR, "data")


def test_load_catalog_small_sky():
    """Instantiate a catalog with 1 pixel"""
    cat = Catalog(os.path.join(TEST_DATA_DIR, "small_sky"))

    assert cat.catalog_name == "small_sky"
    assert len(cat.get_pixels()) == 1
    assert len(cat.get_partitions()) == 1


def test_load_catalog_small_sky_order1():
    """Instantiate a catalog with 4 pixels"""
    cat = Catalog(os.path.join(TEST_DATA_DIR, "small_sky_order1"))

    assert cat.catalog_name == "small_sky_order1"
    assert len(cat.get_pixels()) == 4
    assert len(cat.get_partitions()) == 4
