import json
import os.path

import numpy as np
import pandas as pd
import pytest

from hipscat.io.file_io import get_file_pointer_from_path, make_directory, write_string_to_file, \
    load_json_file, load_csv_to_pandas, write_dataframe_to_csv


def test_make_directory(tmp_path):
    test_dir_path = os.path.join(tmp_path, "test_path")
    assert not os.path.exists(test_dir_path)
    test_dir_pointer = get_file_pointer_from_path(test_dir_path)
    make_directory(test_dir_pointer)
    assert os.path.exists(test_dir_path)


def test_make_existing_directory_raises(tmp_path):
    test_dir_path = os.path.join(tmp_path, "test_path")
    os.makedirs(test_dir_path)
    assert os.path.exists(test_dir_path)
    test_dir_pointer = get_file_pointer_from_path(test_dir_path)
    with pytest.raises(OSError):
        make_directory(test_dir_pointer)


def test_make_existing_directory_existok(tmp_path):
    test_dir_path = os.path.join(tmp_path, "test_path")
    os.makedirs(test_dir_path)
    test_inner_dir_path = os.path.join(test_dir_path, "test_inner")
    os.makedirs(test_inner_dir_path)
    assert os.path.exists(test_dir_path)
    assert os.path.exists(test_inner_dir_path)
    test_dir_pointer = get_file_pointer_from_path(test_dir_path)
    make_directory(test_dir_pointer, exist_ok=True)
    assert os.path.exists(test_dir_path)
    assert os.path.exists(test_inner_dir_path)


def test_write_string_to_file(tmp_path):
    test_file_path = os.path.join(tmp_path, "text_file.txt")
    test_file_pointer = get_file_pointer_from_path(test_file_path)
    test_string = "this is a test"
    write_string_to_file(test_file_pointer, test_string, encoding="utf-8")
    with open(test_file_path, 'r', encoding="utf-8") as file:
        data = file.read().rstrip()
        assert data == test_string


def test_load_json(small_sky_dir):
    catalog_info_path = os.path.join(small_sky_dir, "catalog_info.json")
    json_dict = None
    with open(catalog_info_path, "r", encoding="utf-8") as json_file:
        json_dict = json.load(json_file)
    catalog_info_pointer = get_file_pointer_from_path(catalog_info_path)
    loaded_json_dict = load_json_file(catalog_info_pointer, encoding="utf-8")
    assert loaded_json_dict == json_dict


def test_load_csv_to_pandas(small_sky_dir):
    partition_info_path = os.path.join(small_sky_dir, "partition_info.csv")
    csv_df = pd.read_csv(partition_info_path)
    partition_info_pointer = get_file_pointer_from_path(partition_info_path)
    loaded_df = load_csv_to_pandas(partition_info_pointer)
    pd.testing.assert_frame_equal(csv_df, loaded_df)


def test_write_df_to_csv(tmp_path):
    df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
    test_file_path = os.path.join(tmp_path, "test.csv")
    test_file_pointer = get_file_pointer_from_path(test_file_path)
    write_dataframe_to_csv(df, test_file_pointer, index=False)
    loaded_df = pd.read_csv(test_file_path)
    pd.testing.assert_frame_equal(loaded_df, df)
