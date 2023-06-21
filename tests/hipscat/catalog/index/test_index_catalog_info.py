import dataclasses
import json

import pytest

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.index.index_catalog_info import IndexCatalogInfo
from hipscat.io import file_io


def test_index_catalog_info(
    index_catalog_info, index_catalog_info_with_extra, assert_catalog_info_matches_dict
):
    info = IndexCatalogInfo(**index_catalog_info)
    assert_catalog_info_matches_dict(info, index_catalog_info)

    info = IndexCatalogInfo(**index_catalog_info_with_extra)
    assert_catalog_info_matches_dict(info, index_catalog_info)
    assert_catalog_info_matches_dict(info, index_catalog_info_with_extra)


def test_str(index_catalog_info_with_extra):
    correct_string = ""
    for name, value in index_catalog_info_with_extra.items():
        correct_string += f"  {name} {value}\n"
    cat_info = IndexCatalogInfo(**index_catalog_info_with_extra)
    assert str(cat_info) == correct_string


def test_read_from_file(index_catalog_info_file, assert_catalog_info_matches_dict):
    cat_info_fp = file_io.get_file_pointer_from_path(index_catalog_info_file)
    catalog_info = IndexCatalogInfo.read_from_metadata_file(cat_info_fp)
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "primary_catalog",
        "indexing_column",
        "extra_columns",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    with open(index_catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(catalog_info, catalog_info_json)


def test_required_fields_missing(index_catalog_info):
    required_fields = ["primary_catalog", "indexing_column"]
    for required_field in required_fields:
        assert required_field in IndexCatalogInfo.required_fields
    for field in required_fields:
        init_data = index_catalog_info.copy()
        init_data[field] = None
        with pytest.raises(ValueError, match=field):
            IndexCatalogInfo(**init_data)


def test_type_missing(index_catalog_info):
    init_data = index_catalog_info.copy()
    init_data["catalog_type"] = None
    catalog_info = IndexCatalogInfo(**init_data)
    assert catalog_info.catalog_type == CatalogType.INDEX


def test_wrong_type(index_catalog_info, catalog_info_data):
    with pytest.raises(TypeError, match="unexpected"):
        IndexCatalogInfo(**catalog_info_data)

    with pytest.raises(ValueError, match="type index"):
        init_data = index_catalog_info.copy()
        init_data["catalog_type"] = CatalogType.OBJECT
        IndexCatalogInfo(**init_data)
