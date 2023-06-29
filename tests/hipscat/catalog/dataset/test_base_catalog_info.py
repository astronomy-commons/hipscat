import json

import pytest

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.io import file_io


def test_fields_init(base_catalog_info_data, assert_catalog_info_matches_dict):
    catalog_info = BaseCatalogInfo(**base_catalog_info_data)
    assert_catalog_info_matches_dict(catalog_info, base_catalog_info_data)


def test_required_fields_missing(base_catalog_info_data):
    for field in BaseCatalogInfo.required_fields:
        init_data = base_catalog_info_data.copy()
        init_data[field] = None
        with pytest.raises(ValueError, match=field):
            BaseCatalogInfo(**init_data)


def test_wrong_catalog_type(base_catalog_info_data):
    base_catalog_info_data["catalog_type"] = "wrong_type"
    with pytest.raises(ValueError, match=base_catalog_info_data["catalog_type"]):
        BaseCatalogInfo(**base_catalog_info_data)


def test_str(base_catalog_info_data):
    correct_string = ""
    for name, value in base_catalog_info_data.items():
        correct_string += f"  {name} {value}\n"
    cat_info = BaseCatalogInfo(**base_catalog_info_data)
    assert str(cat_info) == correct_string


def test_read_from_file(base_catalog_info_file, assert_catalog_info_matches_dict):
    base_cat_info_fp = file_io.get_file_pointer_from_path(base_catalog_info_file)
    catalog_info = BaseCatalogInfo.read_from_metadata_file(base_cat_info_fp)
    with open(base_catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
