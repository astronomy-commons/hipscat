import pytest

from hipscat.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.catalog.dataset.catalog_info_factory import create_catalog_info, from_catalog_dir
from hipscat.catalog.index.index_catalog_info import IndexCatalogInfo
from hipscat.catalog.margin_cache.margin_cache_catalog_info import MarginCacheCatalogInfo
from hipscat.catalog.source_catalog.source_catalog_info import SourceCatalogInfo


def test_create_catalog_info_bad(base_catalog_info_data):
    base_catalog_info_data["catalog_type"] = "foo"
    with pytest.raises(ValueError, match="Unknown"):
        create_catalog_info(base_catalog_info_data)

    base_catalog_info_data.pop("catalog_type")
    with pytest.raises(ValueError, match="required"):
        create_catalog_info(base_catalog_info_data)


def test_create_catalog_info(base_catalog_info_data, catalog_info_data):
    catalog_info = create_catalog_info(base_catalog_info_data)
    assert catalog_info.catalog_name == "test_name"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, CatalogInfo)

    catalog_info = create_catalog_info(catalog_info_data)
    assert catalog_info.catalog_name == "test_name"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, CatalogInfo)


def test_create_catalog_info_association(association_catalog_info_data):
    catalog_info = create_catalog_info(association_catalog_info_data)
    assert catalog_info.catalog_name == "test_name"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)


def test_create_catalog_info_source(source_catalog_info, source_catalog_info_with_extra):
    catalog_info = create_catalog_info(source_catalog_info)
    assert catalog_info.catalog_name == "test_source"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, SourceCatalogInfo)

    catalog_info = create_catalog_info(source_catalog_info_with_extra)
    assert catalog_info.catalog_name == "test_source"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, SourceCatalogInfo)


def test_create_catalog_info_margin_cache(margin_cache_catalog_info):
    catalog_info = create_catalog_info(margin_cache_catalog_info)
    assert catalog_info.catalog_name == "test_margin"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, MarginCacheCatalogInfo)


def test_create_catalog_info_index(index_catalog_info, index_catalog_info_with_extra):
    catalog_info = create_catalog_info(index_catalog_info)
    assert catalog_info.catalog_name == "test_index"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, IndexCatalogInfo)

    catalog_info = create_catalog_info(index_catalog_info_with_extra)
    assert catalog_info.catalog_name == "test_index"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, IndexCatalogInfo)


def test_from_catalog_dir_object(small_sky_dir):
    catalog_info = from_catalog_dir(small_sky_dir)
    assert catalog_info.catalog_name == "small_sky"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, CatalogInfo)


def test_from_catalog_dir_source(source_catalog_info_file):
    catalog_info = from_catalog_dir(source_catalog_info_file)
    assert catalog_info.catalog_name == "small_sky_source_catalog"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, SourceCatalogInfo)


def test_from_catalog_dir_margin_cache(margin_cache_catalog_info_file):
    catalog_info = from_catalog_dir(margin_cache_catalog_info_file)
    assert catalog_info.catalog_name == "margin_cache"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, MarginCacheCatalogInfo)


def test_from_catalog_dir_index(index_catalog_info_file):
    catalog_info = from_catalog_dir(index_catalog_info_file)
    assert catalog_info.catalog_name == "index_catalog"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, IndexCatalogInfo)


def test_from_catalog_dir_association(association_catalog_path, association_catalog_info_file):
    catalog_info = from_catalog_dir(association_catalog_path)
    assert catalog_info.catalog_name == "small_sky_to_small_sky_order1"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)

    catalog_info = from_catalog_dir(association_catalog_info_file)
    assert catalog_info.catalog_name == "small_sky_to_small_sky_order1"
    assert isinstance(catalog_info, BaseCatalogInfo)
    assert isinstance(catalog_info, AssociationCatalogInfo)
