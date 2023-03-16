import json
import os

import pandas as pd

from hipscat.io.file_io.file_pointers import FilePointer


def make_directory(file_pointer: FilePointer, exist_ok=False):
    os.makedirs(file_pointer, exist_ok=exist_ok)


def write_string_to_file(file_pointer: FilePointer, json_string: str, encoding: str="utf-8"):
    with open(file_pointer, "w", encoding=encoding) as file:
        file.write(json_string + "\n")


def load_json_file(file_pointer: FilePointer, encoding: str= "utf-8") -> dict:
    with open(file_pointer, "r", encoding=encoding) as json_file:
        json_dict = json.load(json_file)
    return json_dict


def load_csv_to_pandas(file_pointer: FilePointer, **kwargs):
    return pd.read_csv(file_pointer, **kwargs)


def write_dataframe_to_csv(dataframe: pd.DataFrame, file_pointer: FilePointer, **kwargs):
    dataframe.to_csv(file_pointer, **kwargs)
