import os
import pytest

from hipscat.io.file_io import (
    append_paths_to_pointer,
    directory_has_contents,
    does_file_or_directory_exist,
    find_files_matching_path,
    get_basename_from_filepointer,
    get_directory_contents,
    get_file_pointer_from_path,
    is_regular_file,
    get_file_pointer_for_fs,
    get_file_protocol,
    strip_leading_slash_for_pyarrow
)


def test_get_pointer_from_path(tmp_path):
    tmp_pointer = get_file_pointer_from_path(str(tmp_path))
    assert str(tmp_pointer) == str(tmp_path)


def test_get_basename_from_filepointer(tmp_path):
    catalog_info_string = os.path.join(tmp_path, "catalog_info.json")
    catalog_info_pointer = get_file_pointer_from_path(catalog_info_string)
    assert get_basename_from_filepointer(catalog_info_pointer) == "catalog_info.json"


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


def test_get_file_pointer_for_fs():
    test_abfs_protocol_path = get_file_pointer_from_path("abfs:///container/path/to/parquet/file")
    assert get_file_pointer_for_fs("abfs", file_pointer=test_abfs_protocol_path) == "/container/path/to/parquet/file"
    test_s3_protocol_path = get_file_pointer_from_path("s3:///bucket/path/to/catalog.json")
    assert get_file_pointer_for_fs("s3", file_pointer=test_s3_protocol_path) == "/bucket/path/to/catalog.json"
    test_local_path = get_file_pointer_from_path("/path/to/file")
    assert get_file_pointer_for_fs("file", file_pointer=test_local_path) == test_local_path
    test_local_protocol_path = get_file_pointer_from_path("file:///path/to/file")
    assert get_file_pointer_for_fs("file", file_pointer=test_local_protocol_path) == "/path/to/file"

    with pytest.raises(NotImplementedError):
        get_file_protocol("invalid:///path/to/file")
    with pytest.raises(NotImplementedError):
        get_file_pointer_for_fs("invalid", get_file_pointer_from_path("/path/to/file"))


def test_strip_leading_slash_for_pyarrow():
    test_leading_slash_filename = get_file_pointer_from_path("/bucket/path/test.txt")
    assert strip_leading_slash_for_pyarrow(test_leading_slash_filename, protocol="abfs") == "bucket/path/test.txt"
    test_non_leading_slash_filenaem = get_file_pointer_from_path("bucket/path/test.txt")
    assert strip_leading_slash_for_pyarrow(test_non_leading_slash_filenaem, protocol="abfs") == "bucket/path/test.txt"
