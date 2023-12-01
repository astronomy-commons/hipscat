import os

from hipscat.io.file_io import (
    directory_has_contents,
    does_file_or_directory_exist,
    find_files_matching_path,
    get_directory_contents,
    get_file_pointer_from_path,
    is_regular_file,
)


def test_file_or_dir_exist(small_sky_dir_cloud, example_cloud_storage_options):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir_cloud)
    assert does_file_or_directory_exist(small_sky_pointer, storage_options=example_cloud_storage_options)
    catalog_info_string = os.path.join(small_sky_dir_cloud, "catalog_info.json")
    catalog_info_pointer = get_file_pointer_from_path(catalog_info_string)
    assert does_file_or_directory_exist(catalog_info_pointer, storage_options=example_cloud_storage_options)


def test_file_or_dir_exist_false(small_sky_dir_cloud, example_cloud_storage_options):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir_cloud + "incorrect file")
    assert not does_file_or_directory_exist(small_sky_pointer, storage_options=example_cloud_storage_options)


def test_is_regular_file(small_sky_dir_cloud, example_cloud_storage_options):
    partition_info_file = os.path.join(small_sky_dir_cloud, "catalog_info.json")
    assert is_regular_file(partition_info_file, storage_options=example_cloud_storage_options)

    assert not is_regular_file(small_sky_dir_cloud, storage_options=example_cloud_storage_options)

    partition_dir = os.path.join(small_sky_dir_cloud, "Norder=0")
    assert not is_regular_file(partition_dir, storage_options=example_cloud_storage_options)


def test_find_files_matching_path(small_sky_dir_cloud, example_cloud_storage_options):
    ## no_wildcard
    assert (
        len(
            find_files_matching_path(
                small_sky_dir_cloud, "catalog_info.json", storage_options=example_cloud_storage_options
            )
        )
        == 1
    )

    ## wilcard in the name
    assert (
        len(
            find_files_matching_path(
                small_sky_dir_cloud, "*.json", storage_options=example_cloud_storage_options
            )
        )
        == 1
    )


def test_find_files_matching_path_directory(small_sky_order1_dir_cloud, example_cloud_storage_options):
    assert (
        len(
            find_files_matching_path(
                small_sky_order1_dir_cloud, storage_options=example_cloud_storage_options
            )
        )
        == 1
    )

    ## wildcard in directory - will match all files at indicated depth
    assert (
        len(
            find_files_matching_path(
                small_sky_order1_dir_cloud, "*", "*", "*", storage_options=example_cloud_storage_options
            )
        )
        == 4
    )


def test_directory_has_contents(small_sky_order1_dir_cloud, example_cloud_storage_options):
    assert directory_has_contents(small_sky_order1_dir_cloud, storage_options=example_cloud_storage_options)


def test_get_directory_contents(small_sky_order1_dir_cloud, example_cloud_storage_options):
    small_sky_contents = get_directory_contents(
        small_sky_order1_dir_cloud, include_protocol=True, storage_options=example_cloud_storage_options
    )

    expected = [
        "Norder=1",
        "_common_metadata",
        "_metadata",
        "catalog_info.json",
        "point_map.fits",
    ]

    expected = [os.path.join(small_sky_order1_dir_cloud, file_name) for file_name in expected]

    assert small_sky_contents == expected
