import os

from hipscat.io.file_io import (
    append_paths_to_pointer,
    directory_has_contents,
    does_file_or_directory_exist,
    find_files_matching_path,
    get_directory_contents,
    get_file_pointer_from_path,
    is_regular_file,
)


def test_get_pointer_from_path(tmp_path):
    tmp_pointer = get_file_pointer_from_path(str(tmp_path))
    assert str(tmp_pointer) == str(tmp_path)


def test_file_or_dir_exist(small_sky_dir):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir)
    assert does_file_or_directory_exist(small_sky_pointer)
    catalog_info_string = os.path.join(small_sky_dir, "catalog_info.json")
    catalog_info_pointer = get_file_pointer_from_path(catalog_info_string)
    assert does_file_or_directory_exist(catalog_info_pointer)


def test_file_or_dir_exist_false(small_sky_dir):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir + "incorrect file")
    assert not does_file_or_directory_exist(small_sky_pointer)


def test_append_paths_to_pointer(tmp_path):
    test_paths = ["folder", "file.txt"]
    test_path = os.path.join(tmp_path, *test_paths)
    tmp_pointer = get_file_pointer_from_path(str(tmp_path))
    assert append_paths_to_pointer(tmp_pointer, *test_paths) == test_path


def test_is_regular_file(small_sky_dir):
    partition_info_file = os.path.join(small_sky_dir, "partition_info.csv")
    assert is_regular_file(partition_info_file)

    assert not is_regular_file(small_sky_dir)

    partition_dir = os.path.join(small_sky_dir, "Norder=0")
    assert not is_regular_file(partition_dir)


def test_find_files_matching_path(small_sky_dir):
    ## no_wildcard
    assert len(find_files_matching_path(small_sky_dir, "partition_info.csv")) == 1

    ## wilcard in the name
    assert len(find_files_matching_path(small_sky_dir, "*.csv")) == 1


def test_find_files_matching_path_directory(small_sky_order1_dir):
    assert len(find_files_matching_path(small_sky_order1_dir)) == 1

    ## wildcard in directory - will match all files at indicated depth
    assert len(find_files_matching_path(small_sky_order1_dir, "*", "*", "*")) == 4


def test_directory_has_contents(small_sky_order1_dir, tmp_path):
    assert directory_has_contents(small_sky_order1_dir)
    assert not directory_has_contents(tmp_path)


def test_get_directory_contents(small_sky_order1_dir, tmp_path):
    small_sky_contents = get_directory_contents(small_sky_order1_dir)
    assert len(small_sky_contents) == 4

    expected = [
        os.path.join(small_sky_order1_dir, "Norder=1"),
        os.path.join(small_sky_order1_dir, "catalog_info.json"),
        os.path.join(small_sky_order1_dir, "partition_info.csv"),
        os.path.join(small_sky_order1_dir, "point_map.fits"),
    ]

    assert small_sky_contents == expected

    assert len(get_directory_contents(tmp_path)) == 0
