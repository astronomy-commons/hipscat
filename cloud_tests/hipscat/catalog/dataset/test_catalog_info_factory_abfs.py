import pytest
import os

from hipscat.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.catalog.dataset.catalog_info_factory import create_catalog_info, from_catalog_dir
from hipscat.catalog.index.index_catalog_info import IndexCatalogInfo
from hipscat.catalog.margin_cache.margin_cache_catalog_info import MarginCacheCatalogInfo
from hipscat.catalog.source_catalog.source_catalog_info import SourceCatalogInfo


def test_from_catalog_dir_object(example_abfs_path, example_abfs_storage_options):
    small_sky_dir = os.path.join(   
        example_abfs_path, 
        "data",
        "small_sky"
    )
    catalog_info = from_catalog_dir(small_sky_dir, example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, CatalogInfo)


def test_from_catalog_dir_source(example_abfs_path, example_abfs_storage_options):
    source_catalog_info_file = os.path.join(
        example_abfs_path,
        "data",
        "small_sky_source", 
        "catalog_info.json"
    )
    catalog_info = from_catalog_dir(source_catalog_info_file, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky_source_catalog"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, SourceCatalogInfo)


def test_from_catalog_dir_margin_cache(example_abfs_path, example_abfs_storage_options):
    margin_cache_catalog_info_file = os.path.join(
        example_abfs_path,
        "data",
        "margin_cache", "catalog_info.json"
    )
    catalog_info = from_catalog_dir(margin_cache_catalog_info_file, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "margin_cache"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, MarginCacheCatalogInfo)


def test_from_catalog_dir_index(example_abfs_path, example_abfs_storage_options):
    index_catalog_info_file = os.path.join(
        example_abfs_path,
        "data", "index_catalog", "catalog_info.json"
    )
    catalog_info = from_catalog_dir(index_catalog_info_file, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "index_catalog"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, IndexCatalogInfo)


def test_from_catalog_dir_association(example_abfs_path, example_abfs_storage_options):
    association_catalog_path = os.path.join(
        example_abfs_path,
        "data", "small_sky_to_small_sky_order1"
    )
    catalog_info = from_catalog_dir(association_catalog_path, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky_to_small_sky_order1"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)

    association_catalog_info_file = os.path.join(
        example_abfs_path,
        "data", "small_sky_to_small_sky_order1", "catalog_info.json"
    )
    catalog_info = from_catalog_dir(association_catalog_info_file, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky_to_small_sky_order1"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)
