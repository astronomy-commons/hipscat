import pytest
import os

from hipscat.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.catalog.dataset.catalog_info_factory import create_catalog_info, from_catalog_dir
from hipscat.catalog.index.index_catalog_info import IndexCatalogInfo
from hipscat.catalog.margin_cache.margin_cache_catalog_info import MarginCacheCatalogInfo
from hipscat.catalog.source_catalog.source_catalog_info import SourceCatalogInfo


def test_from_catalog_dir_object(small_sky_dir_abfs, example_abfs_storage_options):
    catalog_info = from_catalog_dir(small_sky_dir_abfs, example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, CatalogInfo)


def test_from_catalog_dir_source(source_catalog_info_file_abfs, example_abfs_storage_options):
    catalog_info = from_catalog_dir(source_catalog_info_file_abfs, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky_source_catalog"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, SourceCatalogInfo)


def test_from_catalog_dir_margin_cache(margin_cache_catalog_info_file_abfs, example_abfs_storage_options):
    catalog_info = from_catalog_dir(margin_cache_catalog_info_file_abfs, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "margin_cache"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, MarginCacheCatalogInfo)


def test_from_catalog_dir_index(index_catalog_info_file_abfs, example_abfs_storage_options):
    catalog_info = from_catalog_dir(index_catalog_info_file_abfs, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "index_catalog"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, IndexCatalogInfo)


def test_from_catalog_dir_association(association_catalog_path_abfs, association_catalog_info_file_abfs, example_abfs_storage_options):
    catalog_info = from_catalog_dir(association_catalog_path_abfs, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky_to_small_sky_order1"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)

    catalog_info = from_catalog_dir(association_catalog_info_file_abfs, storage_options=example_abfs_storage_options)
    assert catalog_info.catalog_name == "small_sky_to_small_sky_order1"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)
