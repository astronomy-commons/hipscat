import pytest

from hats.catalog.dataset.table_properties import TableProperties


@pytest.mark.parametrize("data_dir", ["catalog", "dataset", "index_catalog", "margin_cache"])
def test_read_from_file_round_trip(test_data_dir, data_dir, tmp_path):
    dataset_path = test_data_dir / "info_only" / data_dir

    table_properties = TableProperties.read_from_dir(dataset_path)
    table_properties.to_properties_file(tmp_path)
    round_trip_properties = TableProperties.read_from_dir(tmp_path)

    assert table_properties == round_trip_properties


def test_read_from_dir_branches(
    small_sky_dir,
    small_sky_order1_dir,
    association_catalog_path,
    small_sky_source_object_index_dir,
    margin_catalog_path,
    small_sky_source_dir,
):
    TableProperties.read_from_dir(small_sky_dir)
    TableProperties.read_from_dir(small_sky_order1_dir)
    TableProperties.read_from_dir(association_catalog_path)
    TableProperties.read_from_dir(small_sky_source_object_index_dir)
    TableProperties.read_from_dir(margin_catalog_path)
    TableProperties.read_from_dir(small_sky_source_dir)
