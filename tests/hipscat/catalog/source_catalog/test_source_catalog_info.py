import dataclasses
import json

import pytest

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.source_catalog.source_catalog_info import SourceCatalogInfo
from hipscat.io import file_io


def test_source_catalog_info(
    source_catalog_info,
    source_catalog_info_with_extra,
    assert_catalog_info_matches_dict,
):
    info = SourceCatalogInfo(**source_catalog_info)
    assert_catalog_info_matches_dict(info, source_catalog_info)

    info = SourceCatalogInfo(**source_catalog_info_with_extra)
    assert_catalog_info_matches_dict(info, source_catalog_info)
    assert_catalog_info_matches_dict(info, source_catalog_info_with_extra)


def test_str(source_catalog_info_with_extra):
    correct_string = ""
    for name, value in source_catalog_info_with_extra.items():
        correct_string += f"  {name} {value}\n"
    cat_info = SourceCatalogInfo(**source_catalog_info_with_extra)
    assert str(cat_info) == correct_string


def test_read_from_file(source_catalog_info_file, assert_catalog_info_matches_dict):
    cat_info_fp = file_io.get_file_pointer_from_path(source_catalog_info_file)
    catalog_info = SourceCatalogInfo.read_from_metadata_file(cat_info_fp)
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "primary_catalog",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    with open(source_catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(catalog_info, catalog_info_json)


def test_required_fields_missing(source_catalog_info):
    required_fields = ["epoch", "ra_column", "dec_column"]
    for required_field in required_fields:
        assert required_field in SourceCatalogInfo.required_fields
    for field in required_fields:
        init_data = source_catalog_info.copy()
        init_data[field] = None
        with pytest.raises(ValueError, match=field):
            SourceCatalogInfo(**init_data)


def test_type_missing(source_catalog_info):
    init_data = source_catalog_info.copy()
    init_data["catalog_type"] = None
    catalog_info = SourceCatalogInfo(**init_data)
    assert catalog_info.catalog_type == CatalogType.SOURCE


def test_wrong_type(source_catalog_info, catalog_info_data):
    with pytest.raises(ValueError, match="type source"):
        SourceCatalogInfo(**catalog_info_data)

    with pytest.raises(ValueError, match="type source"):
        init_data = source_catalog_info.copy()
        init_data["catalog_type"] = CatalogType.OBJECT
        SourceCatalogInfo(**init_data)
