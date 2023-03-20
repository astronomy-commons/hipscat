import os

from hipscat.io.file_io import get_file_pointer_from_path, does_file_or_directory_exist, \
    append_paths_to_pointer, FilePointer


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
