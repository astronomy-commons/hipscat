from hipscat.io.file_io import get_file_pointer_from_path, does_file_or_directory_exist


def test_file_or_dir_exist(small_sky_dir):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir)
    assert does_file_or_directory_exist(small_sky_pointer)


def test_file_or_dir_exist_false(small_sky_dir):
    small_sky_pointer = get_file_pointer_from_path(small_sky_dir + "incorrect file")
    assert not does_file_or_directory_exist(small_sky_pointer)
